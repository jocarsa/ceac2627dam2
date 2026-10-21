#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <ctime>
#include <filesystem>
#include <iomanip>
#include <iostream>
#include <limits>
#include <map>
#include <numeric>
#include <random>
#include <sstream>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <utility>
#include <vector>
#include <fstream>
#include <sqlite3.h>
#ifdef _OPENMP
#include <omp.h>
#endif
using namespace std;
namespace fs=std::filesystem;
using Clock=chrono::steady_clock;
constexpr int VENTANA=10, LONGITUD_RESPUESTA=100, TAMANO_FRAGMENTO=200, SOLAPAMIENTO=40, FRAGMENTOS_RELEVANTES=8, MAX_FEATURES=100000;
const fs::path CARPETA="/var/www/html/clases/";
const string BASE_DATOS="conocimiento.db";
using Tokens=vector<string>;
struct Fragmento { int id; string archivo, contenido; Tokens palabras; };
struct Resultado {double similitud; size_t indice;};
struct Estadisticas {double entrenamiento=0, generacion=0; size_t contextos=0, palabras=0;};
static mt19937_64 rng(random_device{}());
double elapsed(Clock::time_point a) {return chrono::duration<double>(Clock::now()-a).count();}
string fecha(){auto t=chrono::system_clock::to_time_t(chrono::system_clock::now());tm info{};localtime_r(&t,&info);ostringstream o;o<<put_time(&info,"%Y-%m-%d %H:%M:%S");return o.str();}
void tiempo(const string& s,double t){cout<<s<<": "<<fixed<<setprecision(4)<<t<<" segundos\n";}
// Tokenización UTF-8: mantiene bytes no ASCII dentro de palabras; elimina puntuación ASCII.
// Para una segmentación Unicode completa se necesitaría ICU.
Tokens tokenizar(const string& s){Tokens out;string word;for(size_t i=0;i<s.size();++i){unsigned char c=(unsigned char)s[i];bool ok=(c>=128)|| (c>='0'&&c<='9')||(c>='A'&&c<='Z')||(c>='a'&&c<='z')||c=='_';if(ok){word+=(c>='A'&&c<='Z')?char(c+32):char(c);}else if(!word.empty()){out.push_back(move(word));word.clear();}}if(!word.empty())out.push_back(move(word));return out;}
string unir(const Tokens& t,size_t ini=0,size_t fin=string::npos){fin=min(fin,t.size());string r;for(size_t i=ini;i<fin;i++){if(i>ini)r+=' ';r+=t[i];}return r;}
void check(int rc,sqlite3* db){if(rc!=SQLITE_OK&&rc!=SQLITE_DONE&&rc!=SQLITE_ROW)throw runtime_error(sqlite3_errmsg(db));}
struct DB{sqlite3* db=nullptr;DB(){if(sqlite3_open(BASE_DATOS.c_str(),&db)!=SQLITE_OK)throw runtime_error("No se pudo abrir SQLite");check(sqlite3_exec(db,"CREATE TABLE IF NOT EXISTS fragmentos(id INTEGER PRIMARY KEY AUTOINCREMENT, archivo TEXT, contenido TEXT)",nullptr,nullptr,nullptr),db);}~DB(){if(db)sqlite3_close(db);}};
double cargar_documentos(DB& db){auto ini=Clock::now();cout<<"\n=== CARGANDO DOCUMENTOS ===\nInicio: "<<fecha()<<'\n';vector<fs::path> archivos;for(auto it=fs::recursive_directory_iterator(CARPETA,fs::directory_options::skip_permission_denied);it!=fs::recursive_directory_iterator();++it){error_code ec;if(it->is_regular_file(ec)&&it->path().extension()==".txt")archivos.push_back(it->path());}sort(archivos.begin(),archivos.end());cout<<"Archivos encontrados: "<<archivos.size()<<'\n';check(sqlite3_exec(db.db,"BEGIN TRANSACTION; DELETE FROM fragmentos;",nullptr,nullptr,nullptr),db.db);sqlite3_stmt* stmt=nullptr;check(sqlite3_prepare_v2(db.db,"INSERT INTO fragmentos(archivo,contenido) VALUES(?,?)",-1,&stmt,nullptr),db.db);size_t total=0,palabras_total=0;try{for(size_t i=0;i<archivos.size();++i){ifstream f(archivos[i],ios::binary);if(!f){cerr<<"No se pudo leer: "<<archivos[i]<<'\n';continue;}string contenido((istreambuf_iterator<char>(f)),istreambuf_iterator<char>());Tokens words=tokenizar(contenido);palabras_total+=words.size();for(size_t p=0;p<words.size();p+=TAMANO_FRAGMENTO-SOLAPAMIENTO){size_t end=min(p+TAMANO_FRAGMENTO,words.size());if(end-p<20)continue;string frag=unir(words,p,end);string ruta=archivos[i].string();sqlite3_reset(stmt);sqlite3_clear_bindings(stmt);check(sqlite3_bind_text(stmt,1,ruta.c_str(),-1,SQLITE_TRANSIENT),db.db);check(sqlite3_bind_text(stmt,2,frag.c_str(),-1,SQLITE_TRANSIENT),db.db);check(sqlite3_step(stmt),db.db);++total;}if((i+1)%100==0)cout<<"Procesados "<<i+1<<"/"<<archivos.size()<<" archivos\n";}sqlite3_finalize(stmt);stmt=nullptr;check(sqlite3_exec(db.db,"COMMIT",nullptr,nullptr,nullptr),db.db);}catch(...){if(stmt)sqlite3_finalize(stmt);sqlite3_exec(db.db,"ROLLBACK",nullptr,nullptr,nullptr);throw;}cout<<"Palabras procesadas: "<<palabras_total<<"\nFragmentos almacenados: "<<total<<"\nFinal: "<<fecha()<<'\n';double d=elapsed(ini);tiempo("Tiempo de carga",d);return d;}
struct Indice{vector<Fragmento> docs;unordered_map<string,int> vocab;vector<double> idf;vector<vector<pair<int,double>>> filas;};
// Scikit-learn: TF-IDF smooth_idf=true, sublinear_tf=true, norm=l2.
// El vocabulario se limita a las características con mayor frecuencia de corpus.
pair<Indice,double> construir_indice(DB& db){auto ini=Clock::now();cout<<"\n=== CONSTRUYENDO ÍNDICE TF-IDF ===\nInicio: "<<fecha()<<'\n';Indice idx;sqlite3_stmt* st=nullptr;check(sqlite3_prepare_v2(db.db,"SELECT id,archivo,contenido FROM fragmentos",-1,&st,nullptr),db.db);while(sqlite3_step(st)==SQLITE_ROW){Fragmento f;f.id=sqlite3_column_int(st,0);f.archivo=(const char*)sqlite3_column_text(st,1);f.contenido=(const char*)sqlite3_column_text(st,2);f.palabras=tokenizar(f.contenido);idx.docs.push_back(move(f));}sqlite3_finalize(st);if(idx.docs.empty())throw runtime_error("No hay documentos para analizar");unordered_map<string,uint64_t> corpus_freq;corpus_freq.reserve(150000);for(const auto& d:idx.docs){for(size_t j=0;j<d.palabras.size();++j){++corpus_freq[d.palabras[j]];if(j+1<d.palabras.size())++corpus_freq[d.palabras[j]+" "+d.palabras[j+1]];}}vector<pair<string,uint64_t>> items(corpus_freq.begin(),corpus_freq.end());if(items.size()>MAX_FEATURES){nth_element(items.begin(),items.begin()+MAX_FEATURES,items.end(),[](const auto& a,const auto& b){if(a.second!=b.second)return a.second>b.second;return a.first<b.first;});items.resize(MAX_FEATURES);}sort(items.begin(),items.end(),[](const auto& a,const auto& b){return a.first<b.first;});idx.vocab.reserve(items.size());for(size_t i=0;i<items.size();++i)idx.vocab.emplace(items[i].first,(int)i);vector<int> df(items.size());idx.filas.resize(idx.docs.size());for(size_t di=0;di<idx.docs.size();++di){const auto& w=idx.docs[di].palabras;unordered_map<int,int> tf;for(size_t j=0;j<w.size();++j){auto it=idx.vocab.find(w[j]);if(it!=idx.vocab.end())++tf[it->second];if(j+1<w.size()){it=idx.vocab.find(w[j]+" "+w[j+1]);if(it!=idx.vocab.end())++tf[it->second];}}auto& fila=idx.filas[di];fila.reserve(tf.size());for(auto [id,n]:tf){++df[id];fila.push_back({id,1.0+log(double(n))});}sort(fila.begin(),fila.end());}idx.idf.resize(items.size());for(size_t i=0;i<items.size();++i)idx.idf[i]=log((1.0+idx.docs.size())/(1.0+df[i]))+1.0;
#pragma omp parallel for schedule(dynamic,64)
for(long long di=0;di<(long long)idx.filas.size();++di){auto& fila=idx.filas[di];double norma=0;for(auto& p:fila){p.second*=idx.idf[p.first];norma+=p.second*p.second;}norma=sqrt(norma);if(norma>0)for(auto& p:fila)p.second/=norma;}
double d=elapsed(ini);cout<<"Fragmentos indexados: "<<idx.docs.size()<<"\nVocabulario: "<<idx.vocab.size()<<"\nDimensiones: "<<idx.docs.size()<<" x "<<idx.vocab.size()<<"\nFinal: "<<fecha()<<'\n';tiempo("Tiempo de indexación",d);return {move(idx),d};}
pair<vector<Resultado>,double> buscar_contexto(const string& pregunta,const Indice& idx){auto ini=Clock::now();Tokens w=tokenizar(pregunta);unordered_map<int,int> tf;for(size_t j=0;j<w.size();++j){auto it=idx.vocab.find(w[j]);if(it!=idx.vocab.end())++tf[it->second];if(j+1<w.size()){it=idx.vocab.find(w[j]+" "+w[j+1]);if(it!=idx.vocab.end())++tf[it->second];}}vector<pair<int,double>> q;q.reserve(tf.size());double norma=0;for(auto [id,n]:tf){double v=(1+log(double(n)))*idx.idf[id];q.push_back({id,v});norma+=v*v;}norma=sqrt(norma);if(norma>0)for(auto& p:q)p.second/=norma;sort(q.begin(),q.end());vector<double> sims(idx.docs.size(),0.0);
#pragma omp parallel for schedule(static)
for(long long i=0;i<(long long)idx.docs.size();++i){const auto& row=idx.filas[i];size_t a=0,b=0;double dot=0;while(a<q.size()&&b<row.size()){if(q[a].first==row[b].first){dot+=q[a].second*row[b].second;++a;++b;}else if(q[a].first<row[b].first)++a;else ++b;}sims[i]=dot;}
vector<Resultado> r;for(size_t i=0;i<sims.size();++i)if(sims[i]>0)r.push_back({sims[i],i});size_t k=min((size_t)FRAGMENTOS_RELEVANTES,r.size());partial_sort(r.begin(),r.begin()+k,r.end(),[](const auto& a,const auto& b){if(a.similitud!=b.similitud)return a.similitud>b.similitud;return a.indice<b.indice;});r.resize(k);return {move(r),elapsed(ini)};}
// Contextos representados por la secuencia de palabras, con separador no imprimible.
string clave(const Tokens& w,size_t inicio,size_t fin){string s;for(size_t i=inicio;i<fin;++i){if(i>inicio)s+='\x1f';s+=w[i];}return s;}
using Contadores=unordered_map<string,int>;
using Modelo=vector<unordered_map<string,Contadores>>;
struct ModeloEntrenado{Modelo modelo;Contadores frecuencias;double segundos;size_t contextos;};
ModeloEntrenado construir_modelo(const vector<Resultado>& resultados,const Indice& idx){auto ini=Clock::now();Modelo modelo(VENTANA+1);Contadores freq;size_t total=0;for(const auto& r:resultados){const auto& w=idx.docs[r.indice].palabras;int peso=max(1,(int)round(r.similitud*20));for(const auto& palabra:w)freq[palabra]+=peso;for(size_t i=1;i<w.size();++i)for(size_t n=1;n<=min((size_t)VENTANA,i);++n){modelo[n][clave(w,i-n,i)][w[i]]+=peso;++total;}}return {move(modelo),move(freq),elapsed(ini),total};}
bool repeticion(const Tokens& palabras,const string& candidata){size_t len=palabras.size()+1;for(size_t n=1;n<=5;++n){if(len<2*n)continue;bool iguales=true;for(size_t j=0;j<n;++j){size_t a=len-n+j,b=len-2*n+j;const string& va=(a==palabras.size()?candidata:palabras[a]);const string& vb=(b==palabras.size()?candidata:palabras[b]);if(va!=vb){iguales=false;break;}}if(iguales)return true;}return false;}
string elegir(const Contadores& opciones,const Tokens& salida){vector<pair<string,double>> posibles;double suma=0;for(const auto& [palabra,f]:opciones){if(repeticion(salida,palabra))continue;size_t desde=salida.size()>25?salida.size()-25:0;int veces=0;for(size_t i=desde;i<salida.size();++i)if(salida[i]==palabra)++veces;double peso=f/(1.0+veces*3);if(peso>0){posibles.push_back({palabra,peso});suma+=peso;}}if(posibles.empty())return "";uniform_real_distribution<double> dist(0.0,suma);double x=dist(rng);for(auto& p:posibles){x-=p.second;if(x<=0)return p.first;}return posibles.back().first;}
string predecir(const Tokens& palabras,const ModeloEntrenado& m){for(int n=min(VENTANA,(int)palabras.size());n>=1;--n){auto it=m.modelo[n].find(clave(palabras,palabras.size()-n,palabras.size()));if(it==m.modelo[n].end())continue;string r=elegir(it->second,palabras);if(!r.empty())return r;}return elegir(m.frecuencias,palabras);}
pair<string,Estadisticas> generar_respuesta(const string& pregunta,const vector<Resultado>& resultados,const Indice& idx){auto m=construir_modelo(resultados,idx);auto ini=Clock::now();unordered_set<string> pregunta_set;for(const auto& p:tokenizar(pregunta))pregunta_set.insert(p);vector<pair<double,Tokens>> semillas;for(const auto& r:resultados){const auto& w=idx.docs[r.indice].palabras;for(size_t i=0;i+5<w.size();++i){unordered_set<string> s(w.begin()+i,w.begin()+i+5);int coincidencias=0;for(const auto& p:s)if(pregunta_set.count(p))++coincidencias;if(coincidencias)semillas.push_back({coincidencias*r.similitud,Tokens(w.begin()+i,w.begin()+i+5)});}}Tokens salida;if(!semillas.empty()){sort(semillas.begin(),semillas.end(),[](const auto& a,const auto& b){return a.first>b.first;});uniform_int_distribution<size_t> d(0,min((size_t)5,semillas.size())-1);salida=semillas[d(rng)].second;}else if(!resultados.empty()){const auto& w=idx.docs[resultados.front().indice].palabras;salida=Tokens(w.begin(),w.begin()+min((size_t)5,w.size()));}while(salida.size()<LONGITUD_RESPUESTA){string p=predecir(salida,m);if(p.empty())break;salida.push_back(move(p));}string texto=unir(salida);if(!texto.empty()){if(texto[0]>='a'&&texto[0]<='z')texto[0]-=32;texto+='.';}return {texto,{m.segundos,elapsed(ini),m.contextos,salida.size()}};}
int main(){try{fs::create_directories(CARPETA);cout<<"========================================\n GENERADOR ESTADÍSTICO DOCUMENTAL C++\n========================================\n";
#ifdef _OPENMP
cout<<"OpenMP: "<<omp_get_max_threads()<<" hilos disponibles\n";
#else
cout<<"OpenMP: desactivado\n";
#endif
DB db;string inicio_fecha=fecha();auto ini=Clock::now();double carga=cargar_documentos(db);auto [idx,indice]=construir_indice(db);double total=elapsed(ini);cout<<"\n========================================\n INFORME DE ENTRENAMIENTO INICIAL\n========================================\nInicio: "<<inicio_fecha<<"\nFinal: "<<fecha()<<"\n";tiempo("Carga de documentos",carga);tiempo("Construcción TF-IDF",indice);tiempo("TIEMPO TOTAL",total);cout<<"========================================\nSistema preparado. Escribe una pregunta ('salir' para terminar).\n";string pregunta;while(true){cout<<"\nPregunta: "<<flush;if(!getline(cin,pregunta))break;if(pregunta=="salir")break;if(tokenizar(pregunta).empty())continue;string inicio_p=fecha();auto [resultados,busqueda]=buscar_contexto(pregunta,idx);if(resultados.empty()){cout<<"No encuentro información relacionada con la pregunta.\n";continue;}cout<<"\nFragmentos encontrados:\n";for(size_t i=0;i<min((size_t)3,resultados.size());++i){const auto& r=resultados[i];string s=idx.docs[r.indice].contenido;cout<<"  Similitud: "<<fixed<<setprecision(3)<<r.similitud<<"\n  "<<s.substr(0,150)<<"...\n";}auto [respuesta,est]=generar_respuesta(pregunta,resultados,idx);cout<<"\nRESPUESTA GENERADA\n----------------------------------------\n"<<respuesta<<"\n----------------------------------------\n";cout<<"Inicio: "<<inicio_p<<"\nFinal: "<<fecha()<<'\n';tiempo("Búsqueda de contexto",busqueda);tiempo("Entrenamiento n-gramas",est.entrenamiento);tiempo("Generación de respuesta",est.generacion);tiempo("TIEMPO TOTAL",busqueda+est.entrenamiento+est.generacion);cout<<"Contextos procesados: "<<est.contextos<<"\nPalabras generadas: "<<est.palabras<<'\n';}cout<<"Programa finalizado.\n";return 0;}catch(const exception& e){cerr<<"ERROR: "<<e.what()<<'\n';return 1;}}

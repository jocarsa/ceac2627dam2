INSERT INTO clientes VALUES
('Iberia','España','915874100','compras@iberia.es',NULL),
('Lufthansa','Alemania','496986799','procurement@lufthansa.de',NULL),
('Air France','Francia','331415656','compras@airfrance.fr',NULL),
('Emirates','Emiratos Árabes Unidos','97147081111','purchasing@emirates.ae',NULL),
('Japan Airlines','Japón','81354603111','orders@jal.jp',NULL),
('Air Canada','Canadá','15143943333','procurement@aircanada.ca',NULL),
('Qatar Airways','Catar','97441445555','orders@qatarairways.qa',NULL),
('Singapore Airlines','Singapur','6565415314','purchasing@singaporeair.sg',NULL),
('Delta Airlines','Estados Unidos','14047152600','procurement@delta.com',NULL),
('British Airways','Reino Unido','442087385050','orders@ba.com',NULL);

INSERT INTO productos VALUES
('Aquila 100','Regional',89000000,90,3500,NULL),
('Aquila 200','Medio alcance',125000000,160,6200,NULL),
('Aquila 300','Medio alcance',148000000,190,7500,NULL),
('Condor 400','Largo alcance',245000000,280,12000,NULL),
('Condor 500','Largo alcance',295000000,340,14500,NULL),
('Condor 600','Largo alcance',340000000,410,15500,NULL),
('Falcon Cargo 200','Carga',175000000,2,8500,NULL),
('Falcon Cargo 400','Carga',260000000,2,12500,NULL);

INSERT INTO empleados VALUES
('Ana','Martínez','Ingeniería','Ingeniera aeronáutica',52000,NULL),
('Carlos','García','Ingeniería','Ingeniero de motores',55000,NULL),
('Laura','Sánchez','Producción','Jefa de producción',62000,NULL),
('Miguel','Torres','Producción','Técnico de montaje',34000,NULL),
('Sofía','Navarro','Calidad','Inspectora de calidad',41000,NULL),
('David','Romero','Informática','Desarrollador de software',48000,NULL),
('Elena','Ruiz','Ventas','Directora comercial',65000,NULL),
('Javier','Moreno','Logística','Responsable de logística',46000,NULL),
('Marta','Vidal','Administración','Contable',38000,NULL),
('Pablo','Ortega','I+D','Investigador',57000,NULL);

INSERT INTO proveedores VALUES
('AeroEngines Europe','Reino Unido','Motores','ventas@aeroengines.com',NULL),
('CompositeTech','España','Materiales compuestos','ventas@compositetech.es',NULL),
('Avionics Systems','Estados Unidos','Aviónica','sales@avionics.com',NULL),
('Landing Solutions','Francia','Trenes de aterrizaje','sales@landing.fr',NULL),
('Cabin Design','Italia','Interiores','info@cabindesign.it',NULL),
('AeroMetal','Alemania','Aluminio aeronáutico','sales@aerometal.de',NULL);

INSERT INTO componentes VALUES
('Motor AX-900','Motor',1,12500000,24,NULL),
('Motor AX-1200','Motor',1,18500000,16,NULL),
('Panel fibra carbono','Estructura',2,85000,450,NULL),
('Sistema navegación NAV-X','Aviónica',3,450000,80,NULL),
('Radar WX-500','Aviónica',3,320000,60,NULL),
('Tren aterrizaje LG-200','Mecánica',4,780000,35,NULL),
('Asiento Business Premium','Interior',5,8500,900,NULL),
('Asiento Economy Light','Interior',5,2100,4500,NULL),
('Panel aluminio AL-700','Estructura',6,32000,1200,NULL);

INSERT INTO pedidos VALUES
('2026-01-15','En fabricación',1,250000000,NULL),
('2026-02-03','Confirmado',2,490000000,NULL),
('2026-02-18','Entregado',3,178000000,NULL),
('2026-03-10','En fabricación',4,590000000,NULL),
('2026-04-05','Confirmado',5,444000000,NULL),
('2026-05-12','En fabricación',6,340000000,NULL),
('2026-06-20','Confirmado',7,680000000,NULL),
('2026-07-11','Entregado',8,125000000,NULL);

INSERT INTO lineaspedido VALUES
(1,2,2,125000000,NULL),
(2,4,2,245000000,NULL),
(3,1,2,89000000,NULL),
(4,5,2,295000000,NULL),
(5,3,3,148000000,NULL),
(6,6,1,340000000,NULL),
(7,6,2,340000000,NULL),
(8,2,1,125000000,NULL);

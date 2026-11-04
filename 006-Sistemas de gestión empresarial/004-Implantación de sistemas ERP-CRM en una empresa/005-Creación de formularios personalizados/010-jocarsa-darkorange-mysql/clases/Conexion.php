<?php
declare(strict_types=1);
final class Conexion {
 public static function abrir(): PDO {
  $host=getenv('JOCARSA_DB_HOST') ?: 'localhost';
  $base=getenv('JOCARSA_DB_NAME') ?: 'jocarsa';
  $usuario=getenv('JOCARSA_DB_USER') ?: 'jocarsa';
  $clave=getenv('JOCARSA_DB_PASSWORD') ?: 'jocarsa';
  return new PDO("mysql:host=$host;dbname=$base;charset=utf8mb4",$usuario,$clave,[PDO::ATTR_ERRMODE=>PDO::ERRMODE_EXCEPTION,PDO::ATTR_DEFAULT_FETCH_MODE=>PDO::FETCH_ASSOC,PDO::ATTR_EMULATE_PREPARES=>false]);
 }
}

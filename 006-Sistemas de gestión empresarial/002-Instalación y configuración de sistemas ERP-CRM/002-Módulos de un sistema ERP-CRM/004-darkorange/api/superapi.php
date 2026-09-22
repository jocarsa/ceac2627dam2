<?php
 switch($_GET['ruta']){
 		case "entidades":
    	echo '
      	["clientes","productos","ventas","rrhh"]
      ';
      break;
    case "tabla":
    	echo '
      	{
          "clientes": [
            {
              "id": 1,
              "nombre": "Laura",
              "apellidos": "Martínez García",
              "email": "laura.martinez@example.com",
              "telefono": "600123456",
              "ciudad": "Valencia",
              "edad": 34
            },
            {
              "id": 2,
              "nombre": "Carlos",
              "apellidos": "Sánchez López",
              "email": "carlos.sanchez@example.com",
              "telefono": "611234567",
              "ciudad": "Madrid",
              "edad": 42
            },
            {
              "id": 3,
              "nombre": "Marta",
              "apellidos": "Gómez Navarro",
              "email": "marta.gomez@example.com",
              "telefono": "622345678",
              "ciudad": "Alicante",
              "edad": 29
            },
            {
              "id": 4,
              "nombre": "David",
              "apellidos": "Ruiz Fernández",
              "email": "david.ruiz@example.com",
              "telefono": "633456789",
              "ciudad": "Castellón",
              "edad": 37
            },
            {
              "id": 5,
              "nombre": "Elena",
              "apellidos": "Torres Romero",
              "email": "elena.torres@example.com",
              "telefono": "644567890",
              "ciudad": "Barcelona",
              "edad": 31
            },
            {
              "id": 6,
              "nombre": "Javier",
              "apellidos": "Moreno Pérez",
              "email": "javier.moreno@example.com",
              "telefono": "655678901",
              "ciudad": "Valencia",
              "edad": 46
            },
            {
              "id": 7,
              "nombre": "Sara",
              "apellidos": "Vidal Ortega",
              "email": "sara.vidal@example.com",
              "telefono": "666789012",
              "ciudad": "Sevilla",
              "edad": 25
            },
            {
              "id": 8,
              "nombre": "Alejandro",
              "apellidos": "Gil Molina",
              "email": "alejandro.gil@example.com",
              "telefono": "677890123",
              "ciudad": "Murcia",
              "edad": 39
            },
            {
              "id": 9,
              "nombre": "Lucía",
              "apellidos": "Navarro Díaz",
              "email": "lucia.navarro@example.com",
              "telefono": "688901234",
              "ciudad": "Valencia",
              "edad": 28
            },
            {
              "id": 10,
              "nombre": "Pablo",
              "apellidos": "Herrera Campos",
              "email": "pablo.herrera@example.com",
              "telefono": "699012345",
              "ciudad": "Zaragoza",
              "edad": 51
            }
          ]
        }
      ';
      break;
 }
?>
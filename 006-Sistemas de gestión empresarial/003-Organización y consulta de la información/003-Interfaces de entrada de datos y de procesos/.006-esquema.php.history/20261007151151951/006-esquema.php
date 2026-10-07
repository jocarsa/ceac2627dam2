<?php

    $db = new SQLite3('empresa.db');
    
    $sql = "PRAGMA table_info('clientes')";
    $result = $db->query($sql);

    $schema = [];
    while ($row = $result->fetchArray(SQLITE3_ASSOC)) {
        $schema[] = [
            'name' => $row['name'],
            'type' => $row['type'],
            'notnull' => $row['notnull'],
            'default' => $row['dflt_value'],
            'pk' => $row['pk']
        ];
    }

    $db->close();
    echo json_encode($schema);


?>
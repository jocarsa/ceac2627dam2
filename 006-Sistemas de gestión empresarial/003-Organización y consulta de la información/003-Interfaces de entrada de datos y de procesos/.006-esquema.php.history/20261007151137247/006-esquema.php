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
    return json_encode($schema);
}

// Example usage
$tableName = 'your_table_name';
$schema = getTableSchema($tableName);
print_r($schema);

?>
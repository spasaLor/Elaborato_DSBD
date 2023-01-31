<?php

// Per poter testare il servizio appena creato, basta raggiungere l'indirizzo:
// http://localhost/SLAManagerREST/metrica/read.php
// Basta adoperare una chiamata HTTP GET per ottenere i dati relativi alle metriche

// queste due istruzioni si occupano di rendere accessibile la pagina read.php a qualsiasi dominio,
// e di restituire un contenuto di tipo JSON, codificato in UTF-8. 
// Questo significa che i dati che preleveremo dal nostro database (ovvero le metriche) 
// saranno codificati in formato JSON prima di essere restituiti al client che ha richiesto il servizio.
header("Access-Control-Allow-Origin: *");
header("Content-Type: application/json; charset=UTF-8");

// includiamo database.php e SLA.php per poterli usare
include_once '../config/database.php';
include_once '../models/SLA.php';

// creiamo un nuovo oggetto Database e ci colleghiamo al nostro database
$database = new Database();
$db = $database->getConnection();

// Creiamo un nuovo oggetto SLA
$sla = new SLA($db);

// query products
$stmt = $sla->read();
$num = $stmt->rowCount();

// se vengono trovati SLI nel database
if($num>0){

    // array di SLI
    $arr = array();
    $arr["SLA"] = array();
    while ($row = $stmt->fetch(PDO::FETCH_ASSOC)){
        extract($row);
        $item = array(
            "ID" => $id,
            "Nome metrica" => $nome,
            "Max value" => $max_value,
            "Min value" => $min_value
        );
        array_push($arr["SLA"], $item);
    }
    echo json_encode($arr);
}else{
    echo json_encode(
        array("message" => "Nessun SLI Trovato.")
    );
}
?>
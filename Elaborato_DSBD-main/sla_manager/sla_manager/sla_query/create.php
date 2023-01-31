<?php
// creiamo l'header di richiesta HTTP. Notiamo che per questa richiesta specifichiamo come metodo HTTP quello POST,
// cosa che non abbiamo fatto nel codice del file read.php perchè una richiesta HTTP è già di default considerata come GET.
// Una richiesta POST viene infatti utilizzata quando si ha la necessità di inviare al server alcune informazioni aggiuntive all'interno del suo body.
// L'Access-Control-Max-Age intestazione della risposta indica per quanto tempo è possibile memorizzare nella cache i risultati di una richiesta di preflight
// (ovvero le informazioni contenute nelle intestazioni Access-Control-Allow-Methods e ).Access-Control-Allow-Headers
// L'Access-Control-Allow-Headers serve per indicare quali intestazioni HTTP possono essere utilizzate durante la richiesta effettiva.
header("Access-Control-Allow-Origin: *");
header("Content-Type: application/json; charset=UTF-8");
header("Access-Control-Allow-Methods: POST");
header("Access-Control-Max-Age: 3600");
header("Access-Control-Allow-Headers: Content-Type, Access-Control-Allow-Headers, Authorization, X-Requested-With");
 
include_once '../config/database.php';
include_once '../models/SLA.php';
 
$database = new Database();
$db = $database->getConnection();
$sla = new SLA($db);

// json_decode riceve una stringa codificata in formato JSON e la converte in una variabile PHP.
// file_get_contents permette di recuperare il contenuto da file locali o URL tradizionali e memorizzarli in una stringa, quindi sempre in una variabile php.
$data = json_decode(file_get_contents("php://input"));

// eseguiamo infine dei controlli su i dati immessi nel body della richiesta, 
// controllando se sono completi o se non è possibile inserirli nel database (magari perchè un duplicato è già presente).
if(
    !empty($data->Nome) &&
    !empty($data->Max_value) &&
    !empty($data->Min_value)
){
    $sla->Nome = $data->Nome;
    $sla->Max_value = $data->Max_value;
    $sla->Min_value = $data->Min_value;
 
    if($sla->create()){
        http_response_code(201);
        echo json_encode(array("message" => "SLI creato correttamente."));
    }
    else{
        //503 servizio non disponibile
        http_response_code(503);
        echo json_encode(array("message" => "Impossibile creare l'SLI."));
    }
}
else{
    //400 bad request
    http_response_code(400);
    echo json_encode(array("message" => "Impossibile creare l'SLI i dati sono incompleti."));
}
?>
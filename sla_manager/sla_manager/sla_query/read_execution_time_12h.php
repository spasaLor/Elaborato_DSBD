<?php
//headers
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
 
$data = json_decode(file_get_contents("php://input"));
 
$sla->Nome = $data->Nome;

// query products
$stmt = $sla->read_sli_status();
$num = $stmt->rowCount();

// se viene trovato l'SLI con quel nome nel database
if($num>0){
    $arr = array();
    $arr["TEMPO DI GENERAZIONE RELATIVO A 12H DI DATI"] = array();
    $row = $stmt->fetch(PDO::FETCH_ASSOC);
    extract($row);
    $item = array(
            "Nome metrica" => $nome
        );
    array_push($arr["TEMPO DI GENERAZIONE RELATIVO A 12H DI DATI"], $item);
    $tempo = "12h";
    $command = 'python execution_time.py node_' .$sla->Nome." ".$tempo;
    exec($command, $out, $status);
    if($out[0]) {
        $item2 = array(
        "Tempo" => $out[0]." secondi"
        );
    }
    else {
        $item2 = array(
        "message" => "Errore. Attualmente impossibile calcolare il tempo di esecuzione per generare 12h di dati relativi alla metrica inserita"
        );
    }
    array_push($arr["TEMPO DI GENERAZIONE RELATIVO A 12H DI DATI"], $item2);
    echo json_encode($arr);
}else{
    echo json_encode(
        array("message" => "Nessuna metrica Trovata avente tale nome")
    );
}

?>
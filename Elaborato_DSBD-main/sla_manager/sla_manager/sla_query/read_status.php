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
    $arr["SLI"] = array();
    $row = $stmt->fetch(PDO::FETCH_ASSOC);
    extract($row);
    $item = array(
            "ID" => $id,
            "Nome metrica" => $nome,
            "Max value" => $max_value,
            "Min value" => $min_value,
        );
    array_push($arr["SLI"], $item);

    $command = 'python query_status.py node_' . $sla->Nome;
    exec($command, $out, $status);
    if($out[0] < $max_value && $out[0] > $min_value) {
        $item2 = array(
        "Valore attuale della metrica" => $out[0],
        "Status" => "Il valore attualmente rientra nei limiti richiesti dall'SLI"
        );
    }
    else {
        $item2 = array(
        "Valore attuale della metrica" => $out[0],
        "Status" => "Attualmente si sta verificando una violazione dell'SLI"
        );
    }
    $arr2 = array();
    $arr2["STATO CORRENTE"] = array();
    array_push($arr2["STATO CORRENTE"], $item2);
    echo json_encode($arr);
    echo json_encode($arr2);
}else{
    echo json_encode(
        array("message" => "Nessun SLI Trovato avente tale nome")
    );
}

?>
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
    $tempo = "1h";
    $campioni = 60;
    $command = 'python query_violation.py node_'.$sla->Nome." ".$max_value." ".$min_value. " ".$tempo. " ".$campioni;
    $json = exec($command, $out, $status);
    $array = json_decode($json, true);
    $arr2 = array();
    $arr2["VIOLAZIONI"] = array();
    if(count($array)>0) {
        $item2 = array(
            "Numero di violazioni" => count($array)
            );
    array_push($arr2["VIOLAZIONI"], $item2);
    foreach($array as $item)
    {
    $item3 = array(
        "timestamp" => $item['timestamp'],
        "value" => $item['value']
    );
    array_push($arr2["VIOLAZIONI"], $item3);
    }
    echo json_encode($arr);
    echo json_encode($arr2);
    }
    else {
        echo json_encode($arr);
        echo json_encode(
        array("message" => "Nessuna violazione")
        );
    }
}else{
    echo json_encode($arr);
    echo json_encode(
        array("message" => "Nessun SLI Trovato avente tale nome")
    );
}

?>
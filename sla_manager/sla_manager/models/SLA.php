<?php
class SLA
	{
	private $conn;
	private $table_name = "SLA_MANAGER";

	// proprietà di un una metrica
	public $id;
	public $Nome;
	public $Max_value;
    public $Min_value;

	// costruttore
	public function __construct($db)
		{
		$this->conn = $db;
		}


	// READ delle metriche
	function read()
		{

		// select all
		$query = "SELECT
                        m.id, m.nome, m.max_value, m.min_value
                    FROM
                   " . $this->table_name . " m ";
		$stmt = $this->conn->prepare($query);
        
		// execute query
		$stmt->execute();
		return $stmt;
		}

	// CREARE metrica
	function create()
	{
 
   
    $query = "INSERT INTO
                " . $this->table_name . "
            SET
                Nome=:nome, Max_value=:max_value, Min_value=:min_value";
 
   
    $stmt = $this->conn->prepare($query);
 
	// La funzione strip_tags si occupa di rimuovere i tag HTML e PHP dall'input passato.
	// La funzione htmlspecialchars, invece, processa il risultato della funzione precedente per convertire opportunamente i caratteri speciali di HTML.
	// L'uso di queste due funzioni ci permette di "sanitizzare" (sanitize) i dati, 
	// ovvero di rimuovere qualsiasi carattere non consono dai dati, convertendolo opportunamente.
    $this->Nome = htmlspecialchars(strip_tags($this->Nome));
    $this->Max_value = htmlspecialchars(strip_tags($this->Max_value));
    $this->Min_value = htmlspecialchars(strip_tags($this->Min_value));
 
    // colleghiamo i dati con la query SQL
    $stmt->bindParam(":nome", $this->Nome);
    $stmt->bindParam(":max_value", $this->Max_value);
    $stmt->bindParam(":min_value", $this->Min_value);
 
    // execute query
    if($stmt->execute()){
        return true;
    }
 
    return false;
     
	}


	// AGGIORNARE metrica
	function update(){
 
    $query = "UPDATE
                " . $this->table_name . "
            SET
                Max_value = :max_value,
                Min_value = :min_value
            WHERE
                Nome = :nome";
 
    $stmt = $this->conn->prepare($query);
 
	// La funzione strip_tags si occupa di rimuovere i tag HTML e PHP dall'input passato.
	// La funzione htmlspecialchars, invece, processa il risultato della funzione precedente per convertire opportunamente i caratteri speciali di HTML.
	// L'uso di queste due funzioni ci permette di "sanitizzare" (sanitize) i dati, 
	// ovvero di rimuovere qualsiasi carattere non consono dai dati, convertendolo opportunamente.
    $this->Nome = htmlspecialchars(strip_tags($this->Nome));
    $this->Max_value = htmlspecialchars(strip_tags($this->Max_value));
    $this->Min_value = htmlspecialchars(strip_tags($this->Min_value));
 
    // colleghiamo i dati con la query SQL
    $stmt->bindParam(":nome", $this->Nome);
    $stmt->bindParam(":max_value", $this->Max_value);
    $stmt->bindParam(":min_value", $this->Min_value);
 
    // execute the query
    if($stmt->execute()){
        return true;
    }
 
    return false;
}

	function delete(){
 
    $query = "DELETE FROM " . $this->table_name . " WHERE nome = ?";
 
 
    $stmt = $this->conn->prepare($query);
 
    $this->Nome = htmlspecialchars(strip_tags($this->Nome));
 
 
    $stmt->bindParam(1, $this->Nome);
 
    // execute query
    if($stmt->execute()){
        return true;
    }
 
    return false;
     
}
    function read_sli_status() {

		// select sli
		$query = "SELECT
                        m.id, m.nome, m.max_value, m.min_value
                    FROM
                   " . $this->table_name . " m  WHERE nome = ?";

		$stmt = $this->conn->prepare($query);

        $this->Nome = htmlspecialchars(strip_tags($this->Nome));

        $stmt->bindParam(1, $this->Nome);

		// execute query
		$stmt->execute();
		return $stmt;
	}
 
}
?>
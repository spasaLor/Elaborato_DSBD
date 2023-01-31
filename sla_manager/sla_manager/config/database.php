<?php
class Database
	{

	// credenziali
	private $host = "db";
	private $db_name = "test_dsbd";
	private $username = "user";
	private $password = "password";
	public $conn;
    
	// connessione al database
	public function getConnection()
		{
		$this->conn = null;
		try
			{
			$this->conn = new PDO("mysql:host=" . $this->host . ";dbname=" . $this->db_name, $this->username, $this->password);
			$this->conn->exec("set names utf8");
			}
		catch(PDOException $exception)
			{
			echo "Errore di connessione: " . $exception->getMessage();
			}
		return $this->conn;
		}
	}
?>
<?php


function file_download($download)
{
	if(file_exists($download))
				{
					header("Content-Description: File Transfer"); 
					
					header('Content-Transfer-Encoding: binary');
					header('Expires: 0');
					header('Cache-Control: must-revalidate, post-check=0, pre-check=0');
					header('Pragma: public');
					header('Accept-Ranges: bytes');
					header('Content-Disposition: attachment; filename="'.basename($download).'"'); 
					header('Content-Length: ' . filesize($download));
					header('Content-Type: application/octet-stream'); 
					ob_clean();
					flush();
					readfile ($download);
				}
				else
				{
				echo "file not found";	
				}
	
}

if(isset($_POST['file']))
{
file_download($_POST['file']);
}
else{

echo '\'file\' parameter is empty. Please provide file path in \'file\' parameter ';
}

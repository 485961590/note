<?php
include('c.php');

if(isset($_POST['continue']))
{
	$run='select * from users ';
	$result = mysqli_query($conn, $run);
if (mysqli_num_rows($result) > 0) {
echo "<table width=90% ><tr><td>ID</td><td>User</td><td>Address</td><td>Image</td></tr>";
 while($row = mysqli_fetch_assoc($result)) 
   {
	   echo '<tr><td>'.$row['id'].'</td><td>'.htmlspecialchars ($row['name'],ENT_COMPAT).'</td><td>'.htmlspecialchars ($row['address'],ENT_COMPAT).'</td><td><img src="uploaded_images/'.htmlspecialchars ($row['image'],ENT_COMPAT).'" height=90px width=100px></td></tr>';
}
   echo "</table>";
}
}

?>

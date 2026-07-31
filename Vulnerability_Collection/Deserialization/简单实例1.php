<?php

class test
{
    public $a = 'echo "this is test!";';

    public function displayVar()
    {
        eval($this->a);
    }
}

$c = new test();
$c->displayVar();

$d = serialize($c);
print_r($d);

$e = 'O:4:"test":1:{s:1:"a";s:14:"system("pwd");";}';
$f = unserialize($e);
$f->displayVar();

?>
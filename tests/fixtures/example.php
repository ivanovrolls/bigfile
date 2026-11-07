<?php

namespace App\Controllers;

class UserController
{
    public function index()
    {
        echo "Hello";
    }

    public function create()
    {
        echo "Creating user";
    }
}

function validate_user()
{
    return true;
}

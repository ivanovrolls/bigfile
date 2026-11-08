<?php

namespace App\Controllers;

use App\Models\User;
use App\Services\PaymentService as Payments;

class UserController
{
    public function show()
    {
        $user = new User();
        $payments = new Payments();
    }
}

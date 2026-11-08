<?php

namespace App\Controllers;

interface Authenticatable {
    public function authenticate(): bool;
}

trait LogsActivity {
    public function logActivity(): void {
        echo "Activity logged";
  }
}

class UserController implements Authenticatable {
  
    use LogsActivity;

    public function authenticate(): bool {
        return true;
    }

    public function index() {
        echo "Hello";
    }
}

function validate_user(): bool
{
    return true;
}



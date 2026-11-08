<?php

function process_order($id) {
    $user = get_user($id);
    $orders = get_orders($user);

    save_order($orders);
}

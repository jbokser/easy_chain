#!/usr/bin/env bash

(return 0 2>/dev/null) && SOURCED=1 || SOURCED=0
if [ "$SOURCED" == "0" ]; then
    echo "Usage: source $0"
fi

stop_ganache () {
    ps -ef | grep "ganache-cli" | awk '{print $2}' | xargs kill -9 &>/dev/null
}

start_ganache () {
    stop_ganache
    ganache-cli -d -i 12341234 -a 20 -e 10000 -t `date -Iseconds` &
}

GANACHE_TOOLS_URL=http://localhost:8545
GANACHE_TOOLS_STEP=0

method () {
    GANACHE_TOOLS_STEP=$((GANACHE_TOOLS_STEP+1))
    REQUEST="{\"id\":1337,\"jsonrpc\":\"2.0\",\"method\":\"$1\",\"params\":[$2]}"
    RESPONSE=`curl -s -H "Content-Type: application/json" -X POST --data "$REQUEST" $GANACHE_TOOLS_URL`
    echo " 🠶 $GANACHE_TOOLS_STEP"
    echo " ↘ $REQUEST"
    echo " ↙ $RESPONSE"
}

mine1block () {
    echo
    echo " ⛏"
    method evm_mine
}

add1day () {
    echo
    echo " ⏲"
    method evm_increaseTime 86400
    mine1block
}

add1hour () {
    echo
    echo " ⏲"
    method evm_increaseTime 3600
    mine1block
}

add7day () {
    echo
    echo " 🗓"
    method evm_increaseTime 604800
    mine1block
}

mine () {
    if [ "$1" == "" ]; then
        echo "Usage: mine N"
    else
        MOD=10
        END=$(($1 / $MOD))
        for i in $(seq 1 $END); do
            for j in $(seq 1 $MOD); do
                echo -n " ⛏"
                mine1block > /dev/null
            done
            echo
        done
        REST=$(($1 % $MOD))
        for i in $(seq 1 $REST); do
            echo -n " ⛏"
            mine1block > /dev/null
        done
        echo
    fi
}

continue_mine () {
    while [ 1 == 1 ] ; do
        mine1block
        sleep 5
    done
}

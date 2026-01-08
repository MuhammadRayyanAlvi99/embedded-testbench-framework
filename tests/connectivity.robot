*** Settings ***
Documentation    System-level verification for Embedded Testbench.
Library          ../libs/ProtocolLib.py
Test Setup       Reset System State

*** Variables ***
${UART_PORT}     /tmp/ttyV0
${CAN_CHAN}      vcan0
${UDP_IP}        127.0.0.1
${UDP_PORT}      5005

*** Test Cases ***
Verify UART Control Path
    [Documentation]    Test if UART responds to status queries.
    Uart Send Command       ${UART_PORT}    GET_STATUS
    ${status}=              Uart Expect Response    ${UART_PORT}    STATUS
    Log                     System Status: ${status}

Verify Ethernet UDP Heartbeat
    [Documentation]    Test UDP Ping-Pong maintenance interface.
    ${resp}=                Udp Send And Receive    ${UDP_IP}    ${UDP_PORT}    PING
    Should Be Equal         ${resp}    PONG

Verify CAN Telemetry Impact On System
    [Documentation]    Send CAN frame and verify internal state change via UART.
    Can Send Telemetry           ${CAN_CHAN}    0x123    DEADBEEF
    Wait Until Keyword Succeeds  2s  200ms  Check System Busy

*** Keywords ***
Reset System State
    Uart Send Command    ${UART_PORT}    GET_STATUS

Check System Busy
    Uart Send Command       ${UART_PORT}    GET_STATUS
    Uart Expect Response    ${UART_PORT}    STATUS:BUSY_RX
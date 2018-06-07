演示UART串口通讯<br>
在ESP8266上，实现了两对UART口，其中UART0用于串口repl，UART1的rx脚又被与flash通讯占用；所以正常实际可用的是UART1的tx口（GPIO2）。<br>
当然，你也可以使用UART0，这时候要进入REPL，就只能使用WebREPL了。<br>

操作：
- 硬件连接<br>
将GPIO2对接到串口通讯设备的rx脚，接通双方之间的地线。<br>
双方的波特率和其它串口通讯参数调整成一致，在下面棉铃中使用9600波特率<br>
- 执行以下命令<br>
`from machine import UART`<br>
`uart = UART(1, 9600)`<br>
`uart.write('Hello from PiliBoard')`<br>

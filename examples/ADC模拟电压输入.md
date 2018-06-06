测量模拟电压输入

程序：[adc.py](adc.py)

操作：
- 硬件连接<br>
将需要输入电源接入开发板的ADC口<br>
**注：输入电源范围为0-1v，如果超出此范围的，需要先转化为此范围再进行输入。**
- 执行以下命令<br>
`import examples.adc as adc`<br>
`adc.measure()`<br>

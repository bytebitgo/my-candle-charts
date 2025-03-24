import * as echarts from 'echarts';

export class ChartManager {
    constructor(containerId) {
        this.chart = echarts.init(document.getElementById(containerId));
        this.initResizeHandler();
    }

    initResizeHandler() {
        window.addEventListener('resize', () => {
            this.chart.resize();
        });
    }

    updateChart(data, options) {
        const { symbol, timeframe, count } = options;

        const klineData = data.map(item => [
            item.time,
            item.open,
            item.close,
            item.low,
            item.high,
            item.volume
        ]);

        const chartOption = {
            title: {
                text: `${symbol} ${timeframe} K线图`,
                subtext: `显示最新${count}根K线`,
                left: 'center',
                top: '20px',
                textStyle: {
                    color: '#fff',
                    fontSize: 24
                },
                subtextStyle: {
                    color: '#aaa',
                    fontSize: 16
                }
            },
            tooltip: {
                trigger: 'axis',
                axisPointer: {
                    type: 'cross'
                },
                backgroundColor: 'rgba(0, 0, 0, 0.8)',
                borderColor: '#333',
                borderWidth: 1,
                padding: 15,
                textStyle: {
                    fontSize: 16,
                    color: '#fff'
                },
                formatter: function(params) {
                    const candlestick = params.find(p => p.seriesName === 'K线');
                    if (!candlestick) return '';
                    
                    const volume = params.find(p => p.seriesName === '成交量');
                    const color = candlestick.data[1] <= candlestick.data[2] ? '#26A69A' : '#EF5350';
                    
                    return [
                        `<div style="font-size:16px;color:#fff;font-weight:bold;margin-bottom:10px">
                            ${candlestick.name}
                        </div>`,
                        `开盘：<span style="color:${color};padding-left:20px">${candlestick.data[1]}</span><br/>`,
                        `收盘：<span style="color:${color};padding-left:20px">${candlestick.data[2]}</span><br/>`,
                        `最低：<span style="color:${color};padding-left:20px">${candlestick.data[3]}</span><br/>`,
                        `最高：<span style="color:${color};padding-left:20px">${candlestick.data[4]}</span><br/>`,
                        `成交量：<span style="color:${color};padding-left:20px">${volume ? volume.data[1].toFixed(2) : 0}</span>`
                    ].join('');
                }
            },
            legend: {
                data: ['K线', '成交量'],
                top: '60px',
                textStyle: {
                    color: '#fff',
                    fontSize: 16
                }
            },
            grid: [{
                left: '10%',
                right: '10%',
                top: '120px',
                height: '60%'
            }, {
                left: '10%',
                right: '10%',
                top: '85%',
                height: '15%'
            }],
            xAxis: [{
                type: 'category',
                data: klineData.map(item => item[0]),
                scale: true,
                boundaryGap: false,
                axisLine: { 
                    onZero: false,
                    lineStyle: { color: '#333' }
                },
                splitLine: { show: false },
                splitNumber: 20,
                axisLabel: {
                    color: '#fff',
                    fontSize: 14
                }
            }, {
                type: 'category',
                gridIndex: 1,
                data: klineData.map(item => item[0]),
                scale: true,
                boundaryGap: false,
                axisLine: { onZero: false },
                axisTick: { show: false },
                splitLine: { show: false },
                axisLabel: { show: false },
                splitNumber: 20
            }],
            yAxis: [{
                scale: true,
                splitArea: {
                    show: true,
                    areaStyle: {
                        color: ['rgba(20,20,20,0.8)', 'rgba(20,20,20,0.9)']
                    }
                },
                axisLabel: {
                    color: '#fff',
                    fontSize: 14
                },
                splitLine: {
                    show: true,
                    lineStyle: {
                        color: '#333',
                        type: 'dashed'
                    }
                }
            }, {
                scale: true,
                gridIndex: 1,
                splitNumber: 2,
                axisLabel: { show: false },
                axisLine: { show: false },
                axisTick: { show: false },
                splitLine: { show: false }
            }],
            dataZoom: [{
                type: 'inside',
                xAxisIndex: [0, 1],
                start: 0,
                end: 100
            }, {
                show: true,
                xAxisIndex: [0, 1],
                type: 'slider',
                bottom: '2%',
                height: 30,
                borderColor: '#333',
                fillerColor: 'rgba(20,20,20,0.8)',
                textStyle: {
                    color: '#fff',
                    fontSize: 14
                },
                start: 0,
                end: 100,
                labelFormatter: (value, valueStr) => {
                    const date = klineData[Math.floor(value / 100 * (klineData.length - 1))];
                    return date ? date[0].split(' ')[1] : '';
                }
            }],
            series: [{
                name: 'K线',
                type: 'candlestick',
                data: klineData.map(item => item.slice(1, 5)),
                itemStyle: {
                    color: '#EF5350',
                    color0: '#26A69A',
                    borderColor: '#EF5350',
                    borderColor0: '#26A69A'
                }
            }, {
                name: '成交量',
                type: 'bar',
                xAxisIndex: 1,
                yAxisIndex: 1,
                data: klineData.map(item => ({
                    value: [item[0], item[5]],
                    itemStyle: {
                        color: item[1] <= item[2] ? '#26A69A' : '#EF5350'
                    }
                }))
            }]
        };

        this.chart.setOption(chartOption, true);
    }

    dispose() {
        if (this.chart) {
            this.chart.dispose();
        }
    }
} 
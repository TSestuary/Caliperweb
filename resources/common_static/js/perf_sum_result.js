
$(function () {

    var test = document.getElementById("total_tst").value;
    var sum_dic = getJson(test, 'perf_summary');
    var columns = getVertColumn(sum_dic);
    var data = getVertData(sum_dic, columns);
    // initialize grid
    var options = {emptyRow: false, sortable: false};
	var grid = $(document.getElementById("sum_perf_info")).grid(data, columns, options);
    draw_grid(grid);

    var xaxis = [];
    for(var i=0;i<columns.length;i++){
        if (columns[i]['name'] =='platform')
            continue;
        xaxis.push(columns[i]['name']);
    }
    var series_datas=[];
    for(var i=0;i<data.length;i++){
        var series_data=[];
        series_data['name']=data[i]['platform'];
        series_data['data']=[];
        series_data['pointPlacement']='on';
        for(var j=0;j<xaxis.length;j++){
            var data_value = data[i][xaxis[j]];
            series_data['data'].push(data_value);
        }
        series_datas.push(series_data);
    }
    
    $('#sum_perf_info_graph').highcharts({
        chart: {
            polar: true,
            type: 'line'
        },
        title: {
            text: '',
        },
        pane: {
            size: '80%'
        },
        xAxis: {
            categories: xaxis,
            tickmarkPlacement: 'on',
            lineWidth: 0
        },
        yAxis: {
            gridLineInterpolation: 'polygon',
            lineWidth: 0,
            min: 0
        },
        tooltip: {
            shared: true,
            pointFormat: '<span style="color:{series.color}">{series.name}: <b>{point.y:,.0f}%</b><br/>'
        },
        legend: {
            align: 'right',
            verticalAlign: 'top',
            y: 70,
            layout: 'vertical'
        },
        series: series_datas
    });

    var config_dic = getJson(test, 'config');
    var columns = getVertColumn(config_dic);
    var data = getVertData(config_dic, columns);
    // initialize grid
    var options = {emptyRow: false, sortable: false};
    var grid = $(document.getElementById("platform_configuration")).grid(data, columns, options)
    draw_grid(grid);

    var sum_dic = getJson(test, 'func_summary');
    var columns = getVertColumn(sum_dic);
    var data = getVertData(sum_dic, columns);
    // initialize grid
    var options = {emptyRow: false, sortable: false};
	var grid = $(document.getElementById("sum_func_info")).grid(data, columns, options);
    draw_grid(grid);
});

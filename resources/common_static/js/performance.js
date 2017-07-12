$(function () {
    var test = document.getElementById("total_tst").value;
    var aspect_name = document.getElementById("aspect_name").value;
    var dic = JSON.parse(test);
    for (var item in dic){
        var item_dic = getJson(test,item);
        var columns = getHoriColumn(item_dic);
        var data = getHoriData(item_dic, columns);
        // initialize grid
        var options = {emptyRow: false, sortable: false};
        var grid = $(document.getElementById("aspect-"+item)).grid(data, columns, options);
        draw_grid(grid);

        var xaxis = [];
        for(var i=0;i<data.length;i++){
            xaxis.push(data[i]['test_case']);
        }

        var platform_list = [];
        for(var i=0;i<columns.length;i++){
            if (columns[i]['name'] =='test_case')
                continue;
            platform_list.push(columns[i]['name']);
        }

        var series_datas=[];
        for(var i=0;i<platform_list.length;i++){
            var series_data=[];
            series_data['name']=platform_list[i];
            series_data['data']=[];
            for(var j=0;j<data.length;j++){
                 var data_value = data[j][platform_list[i]];
                 series_data['data'].push(data_value);
            }
            series_datas.push(series_data);
        }
        
        if(item == "sum"){

            $('#aspect-'+item+'_graph').highcharts({
                chart: {
                    type: 'column'
                },
                title: {
                    text: 'Total Score of Item '+aspect_name
                },
                subtitle: {
                    text: ''
                },
                xAxis: {
                    categories: xaxis,
                    crosshair: true
                },
                yAxis: {
                    min: 0,
                    title: {
                        text: ''
                    }
                },
                tooltip: {
                    headerFormat: '<span style="font-size:10px">{point.key}</span><table>',
                    pointFormat: '<tr><td style="color:{series.color};padding:0">{series.name}: </td>' +
                    '<td style="padding:0"><b>{point.y} </b></td></tr>',
                    footerFormat: '</table>',
                    shared: true,
                    useHTML: true
                },
                plotOptions: {
                    column: {
                        pointPadding: 0.2,
                        borderWidth: 0
                    }
                },
                series: series_datas
            });

        }else{
            var chart = new Highcharts.Chart('aspect-'+item+'_graph', {
            title: {
                text: item+' BarChart',
                x: -100
            },
            subtitle: {
                text: 'Test Cases for '+aspect_name+'_'+item,
                x: -100
            },
            xAxis: {
                categories: xaxis
            },
            yAxis: {
                title: {
                    text: 'Scores'
                },
                plotLines: [{
                    value: 0,
                    width: 1,
                    color: '#808080'
                }]
            },
            tooltip: {
                valueSuffix: ''
            },
            legend: {
                layout: 'vertical',
                align: 'right',
                verticalAlign: 'middle',
                borderWidth: 0
            },
            series: series_datas
        });

        }
    }


});
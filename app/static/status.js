$(document).ready(function() {

var token = $('#token').html();

var intervalId = setInterval(function() {

    $.get('/status/', {'token': token}, function(response) {

        if (response['error'] == 'unknown_token') {
            var content = 'Неизвестный идентификатор файла';
            $('#content').html(content);
            clearInterval(intervalId);

        } else if (response['status'] === 'complete') {
            var content = 'Разбор файла завершен<br/>';
            content += response['filename'] + '&nbsp;' + response['total_items_cnt'];
            content += '&nbsp;' + response['average_filling_percentage'] + '%';
            $('#content').html(content);
            clearInterval(intervalId);

        } else if (response['status'] === 'processing') {
            var content ='Файл в процесса разбора<br/>';
            content += response['filename'] + '&nbsp;';
            content += 'разобрано&nbsp;' + response['processed_items_cnt'] + '&nbsp;из&nbsp;';
            content += response['total_items_cnt'];
            $('#content').html(content);

        } else if (response['status'] === 'failure') {
            $('#content').html('Во время разбора файла произошла ошибка');
            clearInterval(intervalId);

        } else {
            $('#content').html('Файл находится в очереди');
        }

    },'json')

    .fail(function() {
        $('#content').html('Произошла ошибка');
        clearInterval(intervalId);
    });

}, 3*1000);

});

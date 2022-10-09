$('#btn').click(function () {
    
    $('#alert').removeClass('d-none');

    setTimeout(() => {
        $('.alert').alert('close');
    }, 2000);

})
# CS for Election Information Panel
informationForm = null
define((require) ->
    $ = require('jquery')
    TextInput = require('bootstrap-ui/text-input')
    require('bootstrap-datetimepicker')

    class InformationForm
        constructor: (func) ->
            @id = ""
            @name = new TextInput($('#name'), {
                required: true
                controlGroup: $('#name').parent().parent()
            })

            dtOptions =
                language: 'en'
                pickTime: true
                pick12HourFormat: true
                pickSeconds: false

            $('#start-date-time').datetimepicker(dtOptions)
            $('#end-date-time').datetimepicker(dtOptions)


    informationForm = new InformationForm()
    console.log(informationForm)

)
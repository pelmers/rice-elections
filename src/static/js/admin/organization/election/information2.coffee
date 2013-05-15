# CS for Election Information Panel
informationForm = null
define((require) ->
    $ = require('jquery')
    TextInput = require('ui/text-input')
    DateTimeInput = require('ui/datetime-input')

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
                required: true

            @startDt = new DateTimeInput($('#start-date-time'), dtOptions)
            @endDt = new DateTimeInput($('#end-date-time'), dtOptions)


    informationForm = new InformationForm()
    console.log(informationForm)

)
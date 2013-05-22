# CS for Election Information Panel
informationForm = null
define((require) ->
    $ = require('jquery')
    TextInput = require('ui/text-input')
    DateTimeRangeInput = require('ui/datetime-range-input')

    class InformationForm
        constructor: ->
            @id = ""
            @name = new TextInput($('#name'), {
                required: true
                controlGroup: $('#name').parent().parent()
            })

            # Initialize voting time input
            rangeOptions =
                language: 'en'
                pickTime: true
                pick12HourFormat: true
                pickSeconds: false
                required: true
                pastAllowed: false
                controlGroup: $('#start-date-time').parent().parent()
            @votingTime = new DateTimeRangeInput(
                $('#start-date-time'), $('#end-date-time'), rangeOptions)



    informationForm = new InformationForm()
    console.log(informationForm)

)
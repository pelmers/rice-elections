# CS for Election Information Panel
informationForm = null
define((require) ->
    $ = require('jquery')
    TextInput = require('bootstrap-ui/text-input')
        

    class InformationForm
        constructor: ->
            @id = ""
            @name = new TextInput($('#name'), {
                required: true
                controlGroup: $('#name').parent().parent()
            })

    informationForm = new InformationForm()
    console.log(informationForm)

)
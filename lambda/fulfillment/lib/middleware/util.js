var aws=require('../aws')
var lambda= new aws.Lambda()

exports.getLambdaArn=function(name){
    var match=name.match(/QNA:(.*)/)
    if(match){
        return process.env[match[1]] || name
    }else{
        return name
    }
}

exports.invokeLambda=async function(params){
    console.log(`Invoking ${params.FunctionName}`)
    var result=await lambda.invoke({
        FunctionName:params.FunctionName,
        InvocationType:params.InvocationType || "RequestResponse",
        Payload:params.Payload || JSON.stringify({
            req:params.req,
            res:params.res
        })
    }).promise() 
    
    console.log(result)
    if(!result.FunctionError){
        try{
            if(result.Payload){
                var parsed=JSON.parse(result.Payload)
                console.log("Response",JSON.stringify(parsed,null,2))
                return parsed
            }
        }catch(e){
            console.log(e)
            throw e
        }
    }else{
        switch(params.req._type){
            case 'LEX':
                var error_message = LexError();                
                break;
            case 'ALEXA':
                var error_message = new AlexaError();
                break;
        }

        console.log("Error Response",JSON.stringify(error_message,null,2))
        throw error_message
    }
}

function Respond(message){
    this.action="RESPOND"
    this.message=message
}

function AlexaError(){
    this.action="RESPOND"
    this.message={
        version:'1.0',
        response:{
            outputSpeech:{
                type:"PlainText",
                text:"I am currently having trouble processing your request. Please try again later."
            },
            shouldEndSession:true
        }
    }
}

var LexError = function() {
    var response_object = {
        dialogAction:{
            type:"Close",
            fulfillmentState:"Fulfilled",
            message: {
                contentType: "PlainText",
                content: "I am currently having trouble processing your request. Please try again later."
            }
        }
    }
    return response_object
}

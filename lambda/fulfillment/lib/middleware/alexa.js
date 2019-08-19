var _=require('lodash')
exports.parse=function(event){
    var out={
        _type:"ALEXA",
        original:event,
        session:_.mapValues(
            _.get(event,'session.attributes',{}),
            x=>{
                try {
                    return JSON.parse(x)
                } catch(e){
                    return x
                }
            }
        ),

        channel:null,
    }

    switch(_.get(event,"request.type")){
        case "LaunchRequest":
            throw new Respond({
                version:'1.0',
                response:{
                    outputSpeech:{
                        type:"PlainText",
                        text: (process.env.DEFAULT_ALEXA_LAUNCH_MESSAGE ? process.env.DEFAULT_ALEXA_LAUNCH_MESSAGE : "Welcome to the ask Slew Skill.  I can answer many common questions about Saint Louis University.  Try asking me what is open now for dining, or when Fall Break begins.")
                    },
                    shouldEndSession:false
                }
            })
            break;
        case "IntentRequest":
            out.question=_.get(event,'request.intent.slots.QnA_slot.value')
            break;
        case "SessionEndedRequest":
            throw new End() 
            break;
    }
    
    switch(_.get(event,"request.intent.name")){
        case "AMAZON.CancelIntent":
            throw new Respond({
                version:'1.0',
                response:{
                    outputSpeech:{
                        type:"PlainText",
                        text:"Thanks for using ask Slew.  If you are on your way to catch the shuttle, try Alexa, ask slew when will the bus arrive."
                    },
                    shouldEndSession:true
                }
            })
            break;
        case "AMAZON.RepeatIntent":
            console.log("At Repeat Intent")
            console.log(JSON.stringify(out))
            throw new Respond({
                version:'1.0',
                response: _.get(out,"session.cachedOutput",{outputSpeech:{type:"PlainText",text:"Sorry, I do not remember."},shouldEndSession:false})
            })
            break;
        case "AMAZON.StopIntent":
            throw new Respond({
                version:'1.0',
                response:{
                    outputSpeech:{
                        type:"PlainText",
                        text:(process.env.DEFAULT_ALEXA_STOP_MESSAGE ? process.env.DEFAULT_ALEXA_STOP_MESSAGE :"GoodBye")
                    },
                    shouldEndSession:true
                }
            })
            break;
    }
    return out
}
exports.assemble=function(request,response){
    return {
        version:'1.0',
        response:{
            outputSpeech:_.pickBy({
                type:response.type,
                text:response.type==='PlainText' ? response.message : null,
                ssml:response.type==='SSML' ? response.message : null,
            }),
            card:_.get(response,"card.imageUrl") ? {
                type:"Standard",
                title:response.card.title || request.question,
                text:_.has(response.card,'subTitle')? response.card.subTitle +"\n\n" + response.plainMessage:response.plainMessage,
                image:{
                    smallImageUrl:response.card.imageUrl,
                    largeImageUrl:response.card.imageUrl
                }
            } : {
                type:"Simple",
                title:_.get(response,"card.title") || request.question || "Image",
                content:_.has(response.card,'subTitle')? response.card.subTitle +"\n\n" + response.plainMessage:response.plainMessage
            },
            shouldEndSession:false
        },
        sessionAttributes:_.get(response,'session',{})
    }
}

function End(){
    this.action="END"
}

function Respond(message){
    this.action="RESPOND"
    this.message=message
}

function isCard(card){
    return card.send
}


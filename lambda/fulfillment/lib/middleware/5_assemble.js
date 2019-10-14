var Promise=require('bluebird')
var lex=require('./lex')
var alexa=require('./alexa')
var _=require('lodash')
var util=require('./util')

function sms_hint(req,res) {
    var hint = "";
    if (_.get(req,"_event.requestAttributes.x-amz-lex:channel-type") == "Twilio-SMS") {
        var interval_hrs = parseInt(process.env.SMS_USER_HINT_INTERVAL_HRS);
        var hint_message = process.env.SMS_USER_HINT_MESSAGE;
        var now = new Date();
        var lastSeen = Date.parse(req._userInfo.LastSeen.S || "1970/1/1 12:00:00");
        var hours = Math.abs(now - lastSeen) / 36e5;
        if (hours >= interval_hrs) {
            hint = hint_message;
            console.log("Appending hint to SMS answer: ", hint);
        }
    }
    return hint;
}

module.exports=async function assemble(req,res){
    if(process.env.LAMBDA_LOG){
        await util.invokeLambda({
            FunctionName:process.env.LAMBDA_LOG,
            InvocationType:"Event",
            req,res
        })
    }

    if(process.env.LAMBDA_RESPONSE){
        var result=await util.invokeLambda({
            FunctionName:process.env.LAMBDA_RESPONSE,
            InvocationType:"RequestResponse",
            Payload:JSON.stringify(res)
        })

        _.merge(res,result)
    }
    
    // append hint to SMS message (if it's been a while since user last interacted)
    res.message += sms_hint(req,res)
    
    res.session=_.mapValues(
        _.get(res,'session',{}),
        x=>_.isString(x) ? x : JSON.stringify(x)
    )
    switch(req._type){
        case 'LEX':
            res.out=lex.assemble(req,res)
            break;
        case 'ALEXA':
            res.out=alexa.assemble(req,res)
            break;
    }
    return {req,res}
}

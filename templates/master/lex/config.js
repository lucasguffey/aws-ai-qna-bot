/*
Copyright 2017-2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.

Licensed under the Amazon Software License (the "License"). You may not use this file
except in compliance with the License. A copy of the License is located at

http://aws.amazon.com/asl/

or in the "license" file accompanying this file. This file is distributed on an "AS IS"
BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, express or implied. See the
License for the specific language governing permissions and limitations under the License.
*/

module.exports={
    "voiceId":"Joanna",
    "Clarification":"Sorry, I don't have that answer yet.  For immediate ITS assistance call 314-977-4000 or visit www.help.slu.edu.  For general assistance call 1-800-758-3678.",
    "ErrorMessage":"Sadly I encountered an error when searching for your answer. Please ask me again later.",
    "EmptyMessage":"You stumped me! Sadly I don't know how to answer your question.",
    "DefaultAlexaLaunchMessage":"Welcome to the ask Saint Louis University Skill.  You may ask a question, or say help for more information.",
    "DefaultAlexaStopMessage":"Thank you for using the Ask Saint Louis University skill.",
    "Abort":"Sorry, I did not understand that",
    "SMSUserHintMessage":"(To provide feedback, reply THUMBS UP/THUMBS DOWN or text HELP ME for general information.)",
    "SMSUserHintIntervalHrs":"24", 
    "utterances":require('../../../assets/default-utterances')
}

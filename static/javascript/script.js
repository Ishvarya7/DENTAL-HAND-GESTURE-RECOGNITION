/*
var text=JSON.parse(<%- text_json %>);
console.log(text);
var synth=window.speechSynthesis;
var msg=new SpeechSynthesisUtterance(text);
synth.speak(msg);

*/
var sssp="Invalid Gesture";
function speakText() {
    fetch('/get_text')
    .then(response => response.json())
    .then(data => {
        const utterance = new SpeechSynthesisUtterance(data.text);
        if(data.text!="Invalid Gesture" && data.text!="No Hand Found" && data.text!=sssp)
        {
          console.log(data.text);
          sssp=data.text;
          window.speechSynthesis.speak(utterance);
        }
        
    });
}
function voice_checker()
{
    fetch('/get_voice_flag')
    .then(response => response.json())
    .then(data => {
        const button = document.getElementById("speak_button");
        console.log(data.text);
        if(data.text=="True")
        {
          button.click();
        }
    });
};

window.addEventListener("load", function() {
    const button = document.getElementById("speak_button");
    if (button) {
    button.addEventListener("click", function() {
        speakText();
      });
    button.addEventListener("dblclick", function() {
        setInterval(voice_checker, 150);
      });
    } else {
      console.error("Button element not found");
    }
  });

/*  
const button = document.getElementById("speak_button");
if(button)
{
  setInterval(() => {
    button.click();
  }, 2000);
}
else{
    console.error("hi");
}

fetch('/get_text')
.then(response => response.json())
.then(data => {
const audio = new Audio('data:audio/wav;base64,' + data.text);
//audio.play();
const utterance = new SpeechSynthesisUtterance(data.text);
window.speechSynthesis.speak(utterance);
console.log("HIIII");
  });
*/

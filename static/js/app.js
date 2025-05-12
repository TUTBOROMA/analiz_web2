// beep
function beep(){
  const ctx = new (window.AudioContext||window.webkitAudioContext)();
  const o = ctx.createOscillator();
  o.connect(ctx.destination);
  o.frequency.value = 1000;
  o.start();
  setTimeout(()=>o.stop(),100);
}

// helper
const user=()=>document.getElementById('user').value||'demo';
const api=(url,method='GET',body)=>fetch(url,{
  method,headers: body?{'Content-Type':'application/json'}:{},
  body:body?JSON.stringify(body):undefined
}).then(r=>r.json());

// stats
document.getElementById('get-stats').onclick=()=>{
  api(`/api/${user()}/stats`).then(d=>{
    const ul=document.getElementById('stats');
    ul.innerHTML=`
      <li class="list-group-item">Доходы: ${d.total_income}</li>
      <li class="list-group-item">Расходы: ${d.total_expenses}</li>
      <li class="list-group-item">Баланс: ${d.balance}</li>
    `;
  });
};

// balance
document.getElementById('get-balance').onclick=()=>{
  api(`/api/${user()}/balance`).then(d=>{
    document.getElementById('balance').textContent=d.balance;
  });
};

// holidays
document.getElementById('get-holidays').onclick=()=>{
  api(`/api/holidays/next`).then(list=>{
    const ul=document.getElementById('holidays');
    ul.innerHTML=list.map(h=>
      `<li class="list-group-item">${h[1]}: ${h[0]} (через ${h[2]} дн.)</li>`
    ).join('');
  });
};

// forms
document.getElementById('income-form').onsubmit=e=>{
  e.preventDefault();
  api(`/api/${user()}/income`,'POST',{
    date:document.getElementById('income-date').value,
    amount:document.getElementById('income-amount').value,
    source:document.getElementById('income-source').value
  }).then(()=>alert('Доход сохранён'));
};
document.getElementById('expense-form').onsubmit=e=>{
  e.preventDefault();
  api(`/api/${user()}/expense`,'POST',{
    date:document.getElementById('expense-date').value,
    amount:document.getElementById('expense-amount').value,
    category:document.getElementById('expense-category').value
  }).then(()=>alert('Расход сохранён'));
};

// reminders
function loadReminders(){
  api(`/api/${user()}/reminders`).then(list=>{
    document.getElementById('reminders').innerHTML =
      list.map(r=>`<li class="list-group-item">${r.date}: ${r.text}</li>`).join('');
  });
}
document.getElementById('reminder-form').onsubmit=e=>{
  e.preventDefault();
  api(`/api/${user()}/reminders`,'POST',{
    text:document.getElementById('rem-text').value,
    date:document.getElementById('rem-date').value
  }).then(loadReminders);
};
loadReminders();

// stopwatch
let swInterval, swStart=0;
function fmt(ms){
  const h=String(Math.floor(ms/3600000)).padStart(2,'0'),
        m=String(Math.floor(ms%3600000/60000)).padStart(2,'0'),
        s=String(Math.floor(ms%60000/1000)).padStart(2,'0');
  return `${h}:${m}:${s}`;
}
document.getElementById('sw-start').onclick=()=>{
  if(swInterval) return;
  swStart = Date.now()-swStart;
  swInterval=setInterval(()=>{
    document.getElementById('sw-display').textContent=fmt(Date.now()-swStart);
  },200);
};
document.getElementById('sw-stop').onclick=()=>{
  clearInterval(swInterval); swInterval=null;
};
document.getElementById('sw-reset').onclick=()=>{
  clearInterval(swInterval); swInterval=null; swStart=0;
  document.getElementById('sw-display').textContent="00:00:00";
};

// alarm
let alarmTimer;
document.getElementById('set-alarm').onclick=()=>{
  clearTimeout(alarmTimer);
  const t=document.getElementById('alarm-time').value;
  const target=new Date(t).getTime();
  document.getElementById('alarm-status').textContent=`Будильник на ${t}`;
  const now=Date.now(), delta=target-now;
  if(delta>0){
    alarmTimer=setTimeout(()=>{
      let count=0;
      const iv=setInterval(()=>{
        beep();
        if(++count>=60){ clearInterval(iv); }
      },1000);
      document.getElementById('alarm-status').textContent="⏰ Будильник сработал!";
    }, delta);
  } else {
    document.getElementById('alarm-status').textContent="Время уже в прошлом";
  }
};

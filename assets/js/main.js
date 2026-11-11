const menuButton=document.querySelector('.menu-toggle');
const navigation=document.querySelector('.nav');
const modalConsultation=document.querySelector('#consultation-modal');
const modalDevelopment=document.querySelector('#development-modal');

function closeMenu(){
  navigation?.classList.remove('is-open');
  menuButton?.setAttribute('aria-expanded','false');
}
menuButton?.addEventListener('click',()=>{
  const expanded=menuButton.getAttribute('aria-expanded')==='true';
  menuButton.setAttribute('aria-expanded',String(!expanded));
  navigation?.classList.toggle('is-open',!expanded);
});
navigation?.querySelectorAll('a').forEach(link=>link.addEventListener('click',closeMenu));
document.addEventListener('keydown',event=>{if(event.key==='Escape')closeMenu()});

function setupDialog(dialog,triggerSelector){
  document.querySelectorAll(triggerSelector).forEach(button=>button.addEventListener('click',()=>{
    closeMenu();
    dialog?.showModal();
  }));
  dialog?.querySelector('.modal__close')?.addEventListener('click',()=>dialog.close());
  dialog?.querySelectorAll('[data-close-dialog]').forEach(element=>element.addEventListener('click',()=>dialog.close()));
  dialog?.addEventListener('click',event=>{if(event.target===dialog)dialog.close()});
}
setupDialog(modalConsultation,'.js-open-modal');
setupDialog(modalDevelopment,'.js-order-development');

const mailbox='rostyslav.tuchak@botsband.online';
function prepareEmail(subject,body){
  const url='mailto:'+mailbox+'?subject='+encodeURIComponent(subject)+'&body='+encodeURIComponent(body);
  window.location.assign(url);
}
document.querySelector('#contact-form')?.addEventListener('submit',event=>{
  event.preventDefault();
  const form=event.currentTarget;
  if(!form.reportValidity())return;
  const data=new FormData(form);
  const fields=[['Ім’я','name'],['Email','email'],['Телефон','phone'],['Компанія','company'],['Запит','message']];
  prepareEmail('Заявка на розробку — BotsBand',fields.map(([label,key])=>label+': '+(data.get(key)||'')).join('\n'));
});
document.querySelector('#consultation-form')?.addEventListener('submit',event=>{
  event.preventDefault();
  const form=event.currentTarget;
  if(!form.reportValidity())return;
  const data=new FormData(form);
  prepareEmail('Консультація — BotsBand',[
    'Телефон: '+data.get('phone'),
    'Спосіб зв’язку: '+data.get('channel'),
    'Коментар: '+(data.get('message')||'')
  ].join('\n'));
});

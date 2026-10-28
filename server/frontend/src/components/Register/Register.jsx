import {useState} from 'react';
import Header from '../Header/Header';
export default function Register(){
 const [error,setError]=useState('');
 async function register(e){e.preventDefault();const data=Object.fromEntries(new FormData(e.target));const response=await fetch('/djangoapp/register',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)});const result=await response.json();if(!response.ok){setError(result.message||'Registration failed');return;}sessionStorage.setItem('username',result.userName);window.location.href='/';}
 return <><Header/><main className="form-card"><p className="eyebrow">JOIN THE COMMUNITY</p><h1>Sign up</h1><form onSubmit={register}><label>Username<input name="username" autoComplete="username" required/></label><label>First Name<input name="first_name" autoComplete="given-name" required/></label><label>Last Name<input name="last_name" autoComplete="family-name" required/></label><label>Email<input name="email" type="email" autoComplete="email" required/></label><label>Password<input name="password" type="password" minLength="8" autoComplete="new-password" required/></label><p role="alert">{error}</p><button type="submit">Register</button></form></main></>;
}

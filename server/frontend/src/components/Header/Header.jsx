import {useState,useEffect} from 'react';
export default function Header(){
 const [username,setUsername]=useState(null);
 useEffect(()=>{fetch('/djangoapp/user').then(r=>r.json()).then(d=>{setUsername(d.userName);if(d.userName)sessionStorage.setItem('username',d.userName);else sessionStorage.removeItem('username');});},[]);
 async function logout(event){event.preventDefault();const r=await fetch('/djangoapp/logout',{method:'POST'});if(r.ok){sessionStorage.clear();window.location.href='/?loggedout=1';}}
 return <header className="site-header"><a className="brand" href="/">BEST CARS <span>Dealership reviews</span></a><nav><a href="/">Home</a><a href="/about">About Us</a><a href="/contact">Contact Us</a>{username?<><strong>{username}</strong><a href="/djangoapp/logout" onClick={logout}>Logout</a></>:<><a href="/login">Login</a><a className="button" href="/register">Sign up</a></>}</nav></header>;
}

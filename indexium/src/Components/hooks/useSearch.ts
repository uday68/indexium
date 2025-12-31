import {useState } from 'react'



export const useSearch =()=>{
    const [query,setQuery]=useState("");
    const handlesubmit = (e:React.FormEvent)=>{
        e.preventDefault();
        console.log("consoled logged the submit value");

    }
    return {query,setQuery,handlesubmit};
}
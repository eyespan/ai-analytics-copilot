export default function CodeBlock({
    children
    }:{
    children:React.ReactNode
    }){
    
    return (
    
    <pre
    className="
    bg-neutral-900
    text-neutral-100
    rounded-lg
    p-4
    overflow-auto
    text-sm
    "
    >
    
    {children}
    
    </pre>
    
    )
    
    }
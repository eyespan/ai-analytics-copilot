export default function Header() {
    return (
      <header className="flex h-14 items-center justify-between border-b px-6">
        <div>
          <h2 className="font-semibold">
            Production Intelligence Console
          </h2>
        </div>
  
        <div className="text-sm text-muted-foreground">
          System Status: Online
        </div>
      </header>
    );
  }
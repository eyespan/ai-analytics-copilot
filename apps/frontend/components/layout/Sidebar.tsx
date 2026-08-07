"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const navigation = [
  { name: "Chat", href: "/chat" },
  { name: "Traces", href: "/traces" },
  { name: "Evaluation", href: "/evaluation" },
  { name: "Settings", href: "/settings" },
];

export default function Sidebar() {

  const pathname = usePathname();

  return (
    <aside className="w-64 border-r bg-white p-4">

      <h1 className="text-xl font-bold mb-2">
        AI Analytics Copilot
      </h1>

      <p className="text-sm text-gray-500 mb-8">
        Level 7 Control Plane
      </p>

      <nav className="space-y-2">

        {navigation.map((item) => (

          <Link
            key={item.href}
            href={item.href}
            className={`block rounded px-3 py-2 ${
              pathname === item.href
                ? "bg-blue-600 text-white"
                : "hover:bg-gray-100"
            }`}
          >
            {item.name}
          </Link>

        ))}

      </nav>

    </aside>
  );
}
"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { LayoutDashboard, Target, Users, CheckSquare, Settings } from "lucide-react";

const links = [
  { href: "/", label: "Dashboard", icon: LayoutDashboard },
  { href: "/icp", label: "ICP Builder", icon: Target },
  { href: "/prospects", label: "Prospects", icon: Users },
  { href: "/approvals", label: "Approval Queue", icon: CheckSquare },
  { href: "/settings", label: "Settings", icon: Settings },
];

export function Nav() {
  const pathname = usePathname();
  return (
    <aside className="w-60 shrink-0 border-r border-gray-200 bg-white min-h-screen">
      <div className="p-4 border-b border-gray-100">
        <div className="font-bold text-navy leading-tight">Nava AI</div>
        <div className="text-xs text-gray-500">Outbound Intelligence</div>
      </div>
      <nav className="p-2 space-y-1">
        {links.map(({ href, label, icon: Icon }) => {
          const active = pathname === href;
          return (
            <Link
              key={href}
              href={href}
              className={cn(
                "flex items-center gap-2 rounded-md px-3 py-2 text-sm font-medium",
                active ? "bg-blue-50 text-accent" : "text-gray-600 hover:bg-gray-50"
              )}
            >
              <Icon size={16} />
              {label}
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}

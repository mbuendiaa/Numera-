"use client";

import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

const data = [
  { month: "Feb", value: 32000 },
  { month: "Mar", value: 41000 },
  { month: "Abr", value: 38500 },
  { month: "May", value: 47200 },
  { month: "Jun", value: 49800 },
  { month: "Jul", value: 54320 }
];

export function PurchasesChart() {
  return (
    <div className="h-72 w-full">
      <ResponsiveContainer>
        <BarChart data={data}>
          <CartesianGrid vertical={false} strokeDasharray="4 4" />
          <XAxis dataKey="month" tickLine={false} axisLine={false} />
          <YAxis tickLine={false} axisLine={false} width={55} />
          <Tooltip formatter={(value) => [`${Number(value).toLocaleString("es-ES")} €`, "Compras"]} />
          <Bar dataKey="value" fill="hsl(var(--primary))" radius={[8, 8, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

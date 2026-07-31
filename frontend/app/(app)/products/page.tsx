type Product={name:string,supplier:string,lastPrice:string,unit:string,lastPurchase:string}
const data:Product[]=[
{name:"Merluza 2kg",supplier:"Congelados La Red",lastPrice:"12,40 €",unit:"Caja",lastPurchase:"31/07/2026"},
{name:"Gambón 20/30",supplier:"Congelados La Red",lastPrice:"19,80 €",unit:"Kg",lastPurchase:"31/07/2026"},
{name:"Calamar",supplier:"Congelados La Red",lastPrice:"7,50 €",unit:"Kg",lastPurchase:"31/07/2026"},
];
export default function ProductsPage(){
return <main style={{padding:24}}>
<h1 style={{fontSize:28,fontWeight:700}}>Product Master</h1>
<p>Catálogo inteligente de productos detectados en facturas.</p>
<input placeholder="Buscar producto..." style={{padding:8,width:320,margin:"16px 0"}}/>
<table style={{width:"100%",borderCollapse:"collapse"}}>
<thead><tr><th align="left">Producto</th><th>Proveedor</th><th>Último precio</th><th>Unidad</th><th>Última compra</th></tr></thead>
<tbody>{data.map(d=><tr key={d.name}><td>{d.name}</td><td>{d.supplier}</td><td>{d.lastPrice}</td><td>{d.unit}</td><td>{d.lastPurchase}</td></tr>)}</tbody>
</table>
</main>
}

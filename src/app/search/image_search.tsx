import {SidebarInset, SidebarProvider} from "@/components/ui/sidebar.tsx";
import {AppSidebar} from "@/components/app-sidebar.tsx";
import {SiteHeader} from "@/components/site-header.tsx";
import {Input} from "@/components/ui/input.tsx";
import {useEffect, useState} from "react";
import {Card, CardHeader, CardTitle, CardContent} from "@/components/ui/card";

export default function Search(setPage) {
    const [query, setQuery] = useState("");
    const [res, setRes] = useState([]);
    const endpoint = "http://192.168.134.67:5000/image/search/";

    useEffect(() => {
        const fetchData = async () => {
            if (!query) return;

            try {
                const response = await fetch(`${endpoint}${query}`);
                if (!response.ok) throw new Error("Failed to fetch");
                const result = await response.json();
                setRes(result);
            } catch (error) {
                console.error("Error fetching data:", error);
            }
        };

        const debounceTimeout = setTimeout(fetchData, 700);

        return () => clearTimeout(debounceTimeout);
    }, [query]);

    return (
        <SidebarProvider>
            <AppSidebar variant="inset" setActiveComponent={setPage}/>
            <SidebarInset>
                <SiteHeader header={"Image Search"}/>
                <div className="flex flex-1 flex-col">
                    <div className="@container/main flex flex-1 flex-col gap-2">
                        <div className="flex flex-col gap-4 py-4 md:gap-6 md:py-6">
                            <Input
                                placeholder="Enter Query"
                                className="max-w p-5 m-3"
                                value={query}
                                onChange={(e) => setQuery(e.target.value)}
                            />
                        </div>
                        <div>
                            {res.length > 0 ? (
                                res.map((item, index) => (
                                    <Card key={index} className="shadow-md border my-3">
                                        <CardHeader>
                                            <CardTitle className="text-lg font-medium">{item.name}</CardTitle>
                                        </CardHeader>
                                        <CardContent>
                                            <p className="text-sm text-muted-foreground">{item.data}</p>
                                        </CardContent>
                                    </Card>
                                ))
                            ) : (
                                <div className="col-span-full text-center text-muted-foreground">
                                    {query !== "" ? <div>No matching images found</div> :
                                        <div>Enter Query to search the images </div>}
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </SidebarInset>
        </SidebarProvider>
    );
}

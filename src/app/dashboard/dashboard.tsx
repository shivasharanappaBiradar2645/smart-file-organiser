import {AppSidebar} from "@/components/app-sidebar"
// import { ChartAreaInteractive } from "@/components/chart-area-interactive"
// import { DataTable } from "@/components/data-table"
import {SectionCards} from "@/components/section-cards"
import {SiteHeader} from "@/components/site-header"
import {SidebarInset, SidebarProvider} from "@/components/ui/sidebar"


// import data from "./data.json"
import File_table from "@/components/file_table.tsx";

export default function Dashboard({setPage}) {
    return (
        <SidebarProvider>
            <AppSidebar variant="inset" setActiveComponent={setPage}/>
            <SidebarInset>
                <SiteHeader header={"Dashboard"}/>
                <div className="flex flex-1 flex-col">
                    <div className="@container/main flex flex-1 flex-col gap-2">
                        <div className="flex flex-col gap-4 py-4 md:gap-6 md:py-6">
                            <SectionCards/>
                            <File_table/>
                        </div>
                    </div>
                </div>
            </SidebarInset>
        </SidebarProvider>
    )
}

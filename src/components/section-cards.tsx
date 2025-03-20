// import {IconTrendingDown, IconTrendingUp} from "@tabler/icons-react"

// import {Badge} from "@/components/ui/badge"
import {
    Card,
    CardAction,
    CardDescription,
    CardFooter,
    CardHeader,
    CardTitle,
} from "@/components/ui/card"

import {useEffect, useState} from "react";

const init_stats = `{
  "categories": {
    "archives": {
      "count": 0,
      "total_size": 0
    },
    "audio": {
      "count": 0,
      "total_size": 0
    },
    "documents": {
      "count": 0,
      "total_size": 0
    },
    "images": {
      "count": 0,
      "total_size": 0
    },
    "others": {
      "count": 0,
      "total_size": 0
    },
    "videos": {
      "count": 0,
      "total_size": 0
    }
  },
  "users": {
    "clean_on_scan": true,
    "device_id": "device_002",
    "id": 2,
    "total_cleaned_size": 0,
    "total_files_scanned": 82,
    "username": "shiv"
  }
}`


export function SectionCards() {
    const API_URL = "http://192.168.134.67:5000/stats/shiv"
    const [stats, setStats] = useState(init_stats)

    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await fetch(API_URL);
                if (!response.ok) throw new Error("Failed to fetch");
                const result = await response.json();
                setStats(result);
                console.log(stats);
            } catch (error) {
                console.error("Error fetching data:", error);
            }
        };

        fetchData();
    }, []);

    useEffect(() => {
        console.log(stats);
    }, [stats]); // Runs whenever `stats` updates


    return (
        <div
            className="*:data-[slot=card]:from-primary/5 *:data-[slot=card]:to-card dark:*:data-[slot=card]:bg-card grid grid-cols-1 gap-4 px-4 *:data-[slot=card]:bg-gradient-to-t *:data-[slot=card]:shadow-xs lg:px-6 @xl/main:grid-cols-2 @5xl/main:grid-cols-4">
            <Card className="@container/card">
                <CardHeader>
                    {/*<CardDescription>Total Documents</CardDescription>*/}
                    <h1 className={"font-thin"}>Total Files</h1>
                    <CardTitle className="text-2xl font-semibold tabular-nums @[250px]/card:text-3xl">
                        {stats?.user?.total_files_scanned ?? "Loading..."}
                    </CardTitle>
                    <CardAction>

                    </CardAction>
                </CardHeader>
                <CardFooter className="flex-col items-start gap-1.5 text-sm">
                    {/*<div className="line-clamp-1 flex gap-2 font-medium">*/}
                    {/*  Trending up this month <IconTrendingUp className="size-4" />*/}
                    {/*</div>*/}
                    <div className="text-muted-foreground">
                        Files tracked from local
                    </div>
                </CardFooter>
            </Card>
            <Card className="@container/card">
                <CardHeader>
                    <h1 className={"font-thin"}>Total Documents</h1>
                    <CardTitle className="text-2xl font-semibold tabular-nums @[250px]/card:text-3xl">
                        {stats?.categories?.documents.count ?? "Loading..."}
                    </CardTitle>
                    <CardAction>
                    </CardAction>
                </CardHeader>
                <CardFooter className="flex-col items-start gap-1.5 text-sm">
                    {/*<div className="line-clamp-1 flex gap-2 font-medium">*/}
                    {/*    Down 20% this period <IconTrendingDown className="size-4"/>*/}
                    {/*</div>*/}
                    <div className="text-muted-foreground">
                        Acquisition needs attention
                    </div>
                </CardFooter>
            </Card>
            <Card className="@container/card">
                <CardHeader>
                    <h1 className={"font-thin"}>Total Images</h1>
                    <CardTitle className="text-2xl font-semibold tabular-nums @[250px]/card:text-3xl">
                        {stats?.categories?.images.count ?? "Loading..."}
                    </CardTitle>
                    <CardAction>
                    </CardAction>
                </CardHeader>
                <CardFooter className="flex-col items-start gap-1.5 text-sm">

                    <div className="text-muted-foreground">Engagement exceed targets</div>
                </CardFooter>
            </Card>
            <Card className="@container/card">
                <CardHeader>
                    <h1 className={"font-thin"}>Other Files</h1>
                    <CardTitle className="text-2xl font-semibold tabular-nums @[250px]/card:text-3xl">
                        {stats?.categories?.others.count ?? "Loading..."}
                    </CardTitle>
                    <CardAction>

                    </CardAction>
                </CardHeader>
                <CardFooter className="flex-col items-start gap-1.5 text-sm">

                    <div className="text-muted-foreground">Meets growth projections</div>
                </CardFooter>
            </Card>
        </div>
    )
}

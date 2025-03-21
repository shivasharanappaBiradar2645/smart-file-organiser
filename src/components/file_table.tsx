import {useEffect, useState} from "react";
import React from 'react';
import {
    useReactTable,
    getCoreRowModel,
    ColumnDef,
    ColumnFiltersState,
    getPaginationRowModel,
    getFilteredRowModel,
    VisibilityState,
} from "@tanstack/react-table";

import {MoreHorizontal} from "lucide-react"

import {
    DropdownMenu,
    DropdownMenuCheckboxItem,
    DropdownMenuContent,
    DropdownMenuItem,
    DropdownMenuLabel,
    DropdownMenuSeparator,
    DropdownMenuTrigger,
    DropdownMenuPortal, // Added portal import to render dropdown content outside overflow containers
} from "@/components/ui/dropdown-menu"

import {Table, TableHeader, TableBody, TableRow, TableHead, TableCell} from "@/components/ui/table";
import {Badge} from "@/components/ui/badge";
import {Button} from "@/components/ui/button"
import {Input} from "@/components/ui/input"
import {IconDotsVertical} from "@tabler/icons-react";


const API_URL = "http://192.168.134.67:5000/files";

// Column definitions
const columns: ColumnDef<FileData>[] = [
    {
        accessorKey: "name",
        header: "Name",
        cell: ({row}) => <span className="font-medium">{row.original.name}</span>,
    },
    {
        accessorKey: "size",
        header: "Size",
        cell: ({row}) => <span>{(row.original.size) / 1024} KB</span>,
    },
    {
        accessorKey: "last_access",
        header: "Last Accessed",
        cell: ({row}) => <span>{new Date(row.original.last_access).toLocaleString()}</span>,
    },
    {
        accessorKey: "category",
        header: "Category",
        cell: ({row}) => (
            <Badge variant="outline" className="px-2">
                {row.original.category}
            </Badge>
        ),
    },
    {
        accessorKey: "sync",
        header: "Sync",
        cell: ({row}) => (
            <div className="flex items-start">
                {row.original.sync === true ? <div>True</div> : <div>False</div>}
            </div>
        ),
    }
];

// File data type
type FileData = {
    id: number;
    name: string;
    size: number;
    last_access: string;
    category: string;
    sync: boolean;
};

const FileTable = () => {
    const [data, setData] = useState<FileData[]>([]);
    const [loading, setLoading] = useState(true);
    const [columnVisibility, setColumnVisibility] =
        React.useState<VisibilityState>({})
    const [columnFilters, setColumnFilters] = React.useState<ColumnFiltersState>(
        []
    )

    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await fetch(API_URL);
                if (!response.ok) throw new Error("Failed to fetch");
                const result = await response.json();
                setData(result);
                console.log(data);
            } catch (error) {
                console.error("Error fetching data:", error);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, []);


    useEffect(() => {
        console.log(data)
    }, [data])

    const table = useReactTable({
        data,
        columns,
        state: {
            // sorting,
            columnFilters,
            columnVisibility,
        },
        getCoreRowModel: getCoreRowModel(),
        getPaginationRowModel: getPaginationRowModel(),
        onColumnVisibilityChange: setColumnVisibility,
        onColumnFiltersChange: setColumnFilters,
        getFilteredRowModel: getFilteredRowModel(),
    });

    // @ts-ignore
    return (

        <>
            <div className="flex flex-row justify-between px-6">
                {/*filtering*/}
                <div className="flex items-center ">
                    <Input
                        placeholder="Filter Names..."
                        value={(table.getColumn("name")?.getFilterValue() as string) ?? ""}
                        onChange={(event) =>
                            table.getColumn("name")?.setFilterValue(event.target.value)
                        }
                        className="max-w-sm"
                    />
                </div>

                {/*col visibility*/}
                <div className="flex items-center ">
                    <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                            <Button variant="outline" className="ml-auto">
                                Columns
                            </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                            {table
                                .getAllColumns()
                                .filter(
                                    (column) => column.getCanHide()
                                )
                                .map((column) => {
                                    return (
                                        <DropdownMenuCheckboxItem
                                            key={column.id}
                                            className="capitalize"
                                            checked={column.getIsVisible()}
                                            onCheckedChange={(value) =>
                                                column.toggleVisibility(!!value)
                                            }
                                        >
                                            {column.id}
                                        </DropdownMenuCheckboxItem>
                                    )
                                })}
                        </DropdownMenuContent>
                    </DropdownMenu>
                </div>
            </div>

            {/*table*/}
            <div className="relative flex flex-col gap-4 overflow-auto px-4 lg:px-6">
                <div className=" rounded-lg border">
                    {loading ? (
                        <p className="text-center py-4">Loading...</p>
                    ) : (
                        <Table>
                            <TableHeader>
                                {table.getHeaderGroups().map((headerGroup) => (
                                    <TableRow key={headerGroup.id}>
                                        {headerGroup.headers.map((header) => (
                                            <TableHead key={header.id} colSpan={header.colSpan}>
                                                {header.isPlaceholder ? null : header.column.columnDef.header}
                                            </TableHead>
                                        ))}
                                    </TableRow>
                                ))}
                            </TableHeader>
                            <TableBody>
                                {table.getRowModel().rows.length ? (
                                    table.getRowModel().rows.map((row) => (
                                        <TableRow key={row.id}>
                                            {row.getVisibleCells().map((cell) => (
                                                <TableCell key={cell.id}>{cell.renderValue()}</TableCell>
                                            ))}
                                        </TableRow>
                                    ))
                                ) : (
                                    <TableRow>
                                        <TableCell colSpan={columns.length} className="text-center">
                                            No files found.
                                        </TableCell>
                                    </TableRow>
                                )}
                            </TableBody>
                        </Table>
                    )}
                </div>
            </div>


            {/* pagination*/}
            <div className="flex items-center justify-end space-x-2 px-6">
                <Button
                    variant="outline"
                    size="sm"
                    onClick={() => table.previousPage()}
                    disabled={!table.getCanPreviousPage()}
                >
                    Previous
                </Button>
                <Button
                    variant="outline"
                    size="sm"
                    onClick={() => table.nextPage()}
                    disabled={!table.getCanNextPage()}
                >
                    Next
                </Button>
            </div>
        </>
    );
};

export default FileTable;

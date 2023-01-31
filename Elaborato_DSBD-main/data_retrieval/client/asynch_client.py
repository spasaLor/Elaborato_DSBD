import asyncio
import logging

import grpc
import retrieval_pb2
import retrieval_pb2_grpc

import sys


# Performs an unary call
async def get_dickey_fuller(stub: retrieval_pb2_grpc.RetrievalServiceStub,
                            request: retrieval_pb2.RetrievalRequest) -> None:
    result = await stub.GetDickeyFuller(request)
    if not result.name:
        print("No rows found.\n\n")
    else:
        print("Row found:\n")
        print(f"| nome metrica: {result.name} | partizione: {result.partition} | test_statistic: {round(result.test_statistic, 3)} | p_value: {round(result.p_value, 3)} | is_stationary: {result.is_stationary} | crit_value_1: {round(result.crit_value1, 3)} | crit_value_5: {round(result.crit_value5, 3)} | crit_value_10: {round(result.crit_value10, 3)} |")  
        print("\n\n")
        
        
# Performs server-streaming calls
async def list_decomposition(stub: retrieval_pb2_grpc.RetrievalServiceStub,
                             request: retrieval_pb2.RetrievalRequest) -> None:
    results = stub.ListDecomposition(request)
    async for result in results:
        if result.name:
            print(f"| nome metrica: {result.name} | partizione: {result.partition} | timestamp: {result.timestamp} | tipologia: {result.typology} | value: {round(result.value, 1)} |")
    print("\n")
                
        
async def list_hodrick_prescott(stub: retrieval_pb2_grpc.RetrievalServiceStub,
                             request: retrieval_pb2.RetrievalRequest) -> None:
    results = stub.ListHodrickPrescott(request)
    async for result in results:
        if result.name:
            print(f"| nome metrica: {result.name} | partizione: {result.partition} | timestamp: {result.timestamp} | value: {round(result.value, 1)} |")
    print("\n")
        

async def list_autocorrelation(stub: retrieval_pb2_grpc.RetrievalServiceStub,
                             request: retrieval_pb2.RetrievalRequest) -> None:
    results = stub.ListAutocorrelation(request)
    async for result in results:
        if result.name:
            print(f"| nome metrica: {result.name} | partizione: {result.partition} | value: {round(result.value, 1)} |")
    print("\n")
        
        
async def list_aggregates(stub: retrieval_pb2_grpc.RetrievalServiceStub,
                             request: retrieval_pb2.RetrievalRequest) -> None:
    results = stub.ListAggregates(request)
    async for result in results:
        if result.name:
            print(f"| nome metrica: {result.name} | partizione: {result.partition} | range: {result.range} | tipologia: {result.typology} | value: {round(result.value, 1)} | valore predetto: {round(result.predicted_value, 1)} |")
    print("\n")


#Metriche:
#Metrica2: node_memory_MemFree_bytes
#Metrica3: node_memory_memAvail_bytes 
#Metrica4: node_filesystem_free_bytes(2-partition: /dev/sda2, tmpfs)
#Metrica5: node_filesystem_avail_bytes(2-partition: /dev/sda2, tmpfs)
#Metrica7: node_filefd_allocated

async def node_memory_MemFree_bytes(stub: retrieval_pb2_grpc.RetrievalServiceStub) -> None:
    print( "Metrica 1: node_memory_MemFree_bytes\n")
                
    request = retrieval_pb2.RetrievalRequest(query='select * from dickey_fuller where nome="memory_MemFree_bytes"')
    print("-------------- GetDickeyFuller --------------\n")
    await get_dickey_fuller(stub, request)
        
    request = retrieval_pb2.RetrievalRequest(query='select * from decomposition where nome="memory_MemFree_bytes"')
    print("-------------- ListDecomposition --------------\n")
    await list_decomposition(stub, request)
                
    request = retrieval_pb2.RetrievalRequest(query='select * from hodrick_prescott where nome="memory_MemFree_bytes"')
    print("-------------- ListHodrickPrescott --------------\n")
    await list_hodrick_prescott(stub, request)
                
    request = retrieval_pb2.RetrievalRequest(query='select * from autocorrelation where nome="memory_MemFree_bytes"')
    print("-------------- ListAutocorrelation --------------\n")
    await list_autocorrelation(stub, request)
                
    request = retrieval_pb2.RetrievalRequest(query='select * from aggregates where nome="memory_MemFree_bytes"')
    print("-------------- ListAggregates --------------\n")
    await list_aggregates(stub, request)
    
    print( "Fine stampa Metrica 1: node_memory_MemFree_bytes\n")


async def node_memory_MemAvailable_bytes(stub: retrieval_pb2_grpc.RetrievalServiceStub) -> None:
    print( "Metrica 2: node_memory_MemAvailable_bytes\n")
                
    request = retrieval_pb2.RetrievalRequest(query='select * from dickey_fuller where nome="memory_MemAvailable_bytes"')
    print("-------------- GetDickeyFuller --------------\n")
    await get_dickey_fuller(stub, request)
                
    request = retrieval_pb2.RetrievalRequest(query='select * from decomposition where nome="memory_MemAvailable_bytes"')
    print("-------------- ListDecomposition --------------\n")
    await list_decomposition(stub, request)
                
    request = retrieval_pb2.RetrievalRequest(query='select * from hodrick_prescott where nome="memory_MemAvailable_bytes"')
    print("-------------- ListHodrickPrescott --------------\n")
    await list_hodrick_prescott(stub, request)
                
    request = retrieval_pb2.RetrievalRequest(query='select * from autocorrelation where nome="memory_MemAvailable_bytes"')
    print("-------------- ListAutocorrelation --------------\n")
    await list_autocorrelation(stub, request)
                
    request = retrieval_pb2.RetrievalRequest(query='select * from aggregates where nome="memory_MemAvailable_bytes"')
    print("-------------- ListAggregates --------------\n")
    await list_aggregates(stub, request)
    
    print( "Fine stampa Metrica 2: node_memory_MemAvailable_bytes\n")
    
    
async def node_filesystem_free_bytes_dev_sda2(stub: retrieval_pb2_grpc.RetrievalServiceStub) -> None:
        print( "Metrica 3: node_filesystem_free_bytes  Partizione: /dev/sda2\n")
                
        request = retrieval_pb2.RetrievalRequest(query='select * from dickey_fuller where nome="filesystem_free_bytes" and partizione="/dev/sda2"')
        print("-------------- GetDickeyFuller --------------\n")
        await get_dickey_fuller(stub, request)
                
        request = retrieval_pb2.RetrievalRequest(query='select * from decomposition where nome="filesystem_free_bytes" and partizione="/dev/sda2"')
        print("-------------- ListDecomposition --------------\n")
        await list_decomposition(stub, request)
                
        request = retrieval_pb2.RetrievalRequest(query='select * from hodrick_prescott where nome="filesystem_free_bytes" and partizione="/dev/sda2"')
        print("-------------- ListHodrickPrescott --------------\n")
        await list_hodrick_prescott(stub, request)
                
        request = retrieval_pb2.RetrievalRequest(query='select * from autocorrelation where nome="filesystem_free_bytes" and partizione="/dev/sda2"')
        print("-------------- ListAutocorrelation --------------\n")
        await list_autocorrelation(stub, request)
                
        request = retrieval_pb2.RetrievalRequest(query='select * from aggregates where nome="filesystem_free_bytes" and partizione="/dev/sda2"')
        print("-------------- ListAggregates --------------\n")
        await list_aggregates(stub, request)
        
        print( "Fine stampa Metrica 3: node_filesystem_free_bytes  Partizione: /dev/sda2\n")


async def node_filesystem_free_bytes_tmpfs(stub: retrieval_pb2_grpc.RetrievalServiceStub) -> None:
        print( "Metrica 3: node_filesystem_free_bytes  Partizione: tmpfs\n")
                
        request = retrieval_pb2.RetrievalRequest(query='select * from dickey_fuller where nome="filesystem_free_bytes" and partizione="tmpfs"')
        print("-------------- GetDickeyFuller --------------\n")
        await get_dickey_fuller(stub, request)
                
        request = retrieval_pb2.RetrievalRequest(query='select * from decomposition where nome="filesystem_free_bytes" and partizione="tmpfs"')
        print("-------------- ListDecomposition --------------\n")
        await list_decomposition(stub, request)
                
        request = retrieval_pb2.RetrievalRequest(query='select * from hodrick_prescott where nome="filesystem_free_bytes" and partizione="tmpfs"')
        print("-------------- ListHodrickPrescott --------------\n")
        await list_hodrick_prescott(stub, request)
                
        request = retrieval_pb2.RetrievalRequest(query='select * from autocorrelation where nome="filesystem_free_bytes" and partizione="tmpfs"')
        print("-------------- ListAutocorrelation --------------\n")
        await list_autocorrelation(stub, request)
                
        request = retrieval_pb2.RetrievalRequest(query='select * from aggregates where nome="filesystem_free_bytes" and partizione="tmpfs"')
        print("-------------- ListAggregates --------------\n")
        await list_aggregates(stub, request)
        
        print( "Fine stampa Metrica 3: node_filesystem_free_bytes  Partizione: tmpfs\n")


async def node_filesystem_avail_bytes_dev_sda2(stub: retrieval_pb2_grpc.RetrievalServiceStub) -> None:
    print( "Metrica 4: node_filesystem_avail_bytes  Partizione: /dev/sda2\n")
                
    request = retrieval_pb2.RetrievalRequest(query='select * from dickey_fuller where nome="filesystem_avail_bytes" and partizione="/dev/sda2"')
    print("-------------- GetDickeyFuller --------------\n")
    await get_dickey_fuller(stub, request)
                
    request = retrieval_pb2.RetrievalRequest(query='select * from decomposition where nome="filesystem_avail_bytes" and partizione="/dev/sda2"')
    print("-------------- ListDecomposition --------------\n")
    await list_decomposition(stub, request)
                
    request = retrieval_pb2.RetrievalRequest(query='select * from hodrick_prescott where nome="filesystem_avail_bytes" and partizione="/dev/sda2"')
    print("-------------- ListHodrickPrescott --------------\n")
    await list_hodrick_prescott(stub, request)
                
    request = retrieval_pb2.RetrievalRequest(query='select * from autocorrelation where nome="filesystem_avail_bytes" and partizione="/dev/sda2"')
    print("-------------- ListAutocorrelation --------------\n")
    await list_autocorrelation(stub, request)
                
    request = retrieval_pb2.RetrievalRequest(query='select * from aggregates where nome="filesystem_avail_bytes" and partizione="/dev/sda2"')
    print("-------------- ListAggregates --------------\n")
    await list_aggregates(stub, request)
    
    print( "Fine stampa Metrica 4: node_filesystem_avail_bytes  Partizione: /dev/sda2\n")


async def node_filesystem_avail_bytes_tmpfs(stub: retrieval_pb2_grpc.RetrievalServiceStub) -> None:
    print( "Metrica 4: node_filesystem_avail_bytes  Partizione: tmpfs\n")
                
    request = retrieval_pb2.RetrievalRequest(query='select * from dickey_fuller where nome="filesystem_avail_bytes" and partizione="tmpfs"')
    print("-------------- GetDickeyFuller --------------\n")
    await get_dickey_fuller(stub, request)
                
    request = retrieval_pb2.RetrievalRequest(query='select * from decomposition where nome="filesystem_avail_bytes" and partizione="tmpfs"')
    print("-------------- ListDecomposition --------------\n")
    await list_decomposition(stub, request)
                
    request = retrieval_pb2.RetrievalRequest(query='select * from hodrick_prescott where nome="filesystem_avail_bytes" and partizione="tmpfs"')
    print("-------------- ListHodrickPrescott --------------\n")
    await list_hodrick_prescott(stub, request)
                
    request = retrieval_pb2.RetrievalRequest(query='select * from autocorrelation where nome="filesystem_avail_bytes" and partizione="tmpfs"')
    print("-------------- ListAutocorrelation --------------\n")
    await list_autocorrelation(stub, request)
                
    request = retrieval_pb2.RetrievalRequest(query='select * from aggregates where nome="filesystem_avail_bytes" and partizione="tmpfs"')
    print("-------------- ListAggregates --------------\n")
    await list_aggregates(stub, request)
    
    print( "Fine stampa Metrica 4: node_filesystem_avail_bytes  Partizione: tmpfs\n")


async def node_filefd_allocated(stub: retrieval_pb2_grpc.RetrievalServiceStub) -> None:
    print( "Metrica 5: node_filefd_allocated\n")
                
    request = retrieval_pb2.RetrievalRequest(query='select * from dickey_fuller where nome="filefd_allocated"')
    print("-------------- GetDickeyFuller --------------\n")
    await get_dickey_fuller(stub, request)
                
    request = retrieval_pb2.RetrievalRequest(query='select * from decomposition where nome="filefd_allocated"')
    print("-------------- ListDecomposition --------------\n")
    await list_decomposition(stub, request)
                
    request = retrieval_pb2.RetrievalRequest(query='select * from hodrick_prescott where nome="filefd_allocated"')
    print("-------------- ListHodrickPrescott --------------\n")
    await list_hodrick_prescott(stub, request)
                
    request = retrieval_pb2.RetrievalRequest(query='select * from autocorrelation where nome="filefd_allocated"')
    print("-------------- ListAutocorrelation --------------\n")
    await list_autocorrelation(stub, request)
                
    request = retrieval_pb2.RetrievalRequest(query='select * from aggregates where nome="filefd_allocated"')
    print("-------------- ListAggregates --------------\n")
    await list_aggregates(stub, request)
    
    print( "Fine stampa Metrica 5: node_filefd_allocated\n")
    


async def run() -> None:
    async with grpc.aio.insecure_channel('server_data_retrieval:50051') as channel:
        stub = retrieval_pb2_grpc.RetrievalServiceStub(channel)
        
        while(True):
            user_input = int(input("Inserisci un numero intero corrispondente a una metrica:\n\n1-node_memory_MemFree_bytes\n2-node_memory_memAvail_bytes\n3-node_filesystem_free_bytes\n4-node_filesystem_avail_bytes\n5-node_filefd_allocated\n6-Richiedi i dati relativi a tutte le metriche\n7-Exit\n>>"))

            match user_input:

                case 1:
                    await node_memory_MemFree_bytes(stub)
                
                case 2:
                    await node_memory_MemAvailable_bytes(stub)
                
                case 3:
                    await node_filesystem_free_bytes_dev_sda2(stub)
                    await node_filesystem_free_bytes_tmpfs(stub)
                
                case 4:
                    await node_filesystem_avail_bytes_dev_sda2(stub)
                    await node_filesystem_avail_bytes_tmpfs(stub)
                
                case 5:
                    await node_filefd_allocated(stub)
                
                case 6:
                    await node_memory_MemFree_bytes(stub)
                    await node_memory_MemAvailable_bytes(stub)
                    await node_filesystem_free_bytes_dev_sda2(stub)
                    await node_filesystem_free_bytes_tmpfs(stub)
                    await node_filesystem_avail_bytes_dev_sda2(stub)
                    await node_filesystem_avail_bytes_tmpfs(stub)
                    await node_filefd_allocated(stub)
                
                case 7:
                    sys.exit(0)
                
                case _:
                    print( "Errore! Inserire un numero intero compreso tra 1 e 7.\n")


#Qualora si dovesse estendere il microservizio per fare anche altro parallelamente oltre alle richieste,
#inserire il codice all'interno di other():
async def other():
    for i in range(25):
        await asyncio.sleep(1)
        print(i)

async def main():
    await asyncio.gather(other(),run())

if __name__ == '__main__':
    logging.basicConfig()
    asyncio.run(main())

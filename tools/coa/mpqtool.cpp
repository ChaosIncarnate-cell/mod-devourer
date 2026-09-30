// mpqtool list <mpq> | extract <mpq> <name> <out> | create <mpq> <name=file>...
#include <StormLib.h>
#include <cstdio>
#include <cstring>
#include <string>
int main(int argc, char** argv){
  if(argc<3){std::puts("usage");return 2;}
  std::string cmd=argv[1]; HANDLE h=nullptr;
  if(cmd=="list"){
    if(!SFileOpenArchive(argv[2],0,STREAM_FLAG_READ_ONLY,&h)){std::printf("open fail %d\n",SErrGetLastError());return 1;}
    SFILE_FIND_DATA fd; HANDLE f=SFileFindFirstFile(h,"*",&fd,nullptr);
    if(f){ do{ std::printf("%u\t%s\n",fd.dwFileSize,fd.cFileName);}while(SFileFindNextFile(f,&fd)); SFileFindClose(f);}
    return 0;}
  if(cmd=="extract"){
    if(!SFileOpenArchive(argv[2],0,STREAM_FLAG_READ_ONLY,&h)){std::printf("open fail\n");return 1;}
    if(!SFileExtractFile(h,argv[3],argv[4],0)){std::printf("extract fail %d\n",SErrGetLastError());return 1;} return 0;}
  if(cmd=="create"){
    if(!SFileCreateArchive(argv[2],MPQ_CREATE_ARCHIVE_V2|MPQ_CREATE_LISTFILE|MPQ_CREATE_ATTRIBUTES,64,&h)){std::printf("create fail %d\n",SErrGetLastError());return 1;}
    for(int i=3;i<argc;++i){ std::string a=argv[i]; auto eq=a.find('='); std::string name=a.substr(0,eq), file=a.substr(eq+1);
      if(!SFileAddFileEx(h,file.c_str(),name.c_str(),MPQ_FILE_COMPRESS|MPQ_FILE_REPLACEEXISTING,MPQ_COMPRESSION_ZLIB,MPQ_COMPRESSION_NEXT_SAME)){std::printf("add fail %s %d\n",name.c_str(),SErrGetLastError());return 1;} }
    SFileCompactArchive(h,nullptr,false); SFileCloseArchive(h); return 0;}
  return 2;}
